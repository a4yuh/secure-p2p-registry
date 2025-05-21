# app/transfer.py

import socket
import os

from encryption import (
    generate_session_key,
    encrypt_file,
    decrypt_file,
    encrypt_key_rsa,
    decrypt_key_rsa
)

# === Constants ===
BUFFER_SIZE = 4096


# === Function: Send Encrypted File ===
def send_file(
    original_file_path,
    peer_ip,
    peer_port=5000,
    peer_public_key_path="peer_public.pem",
    progress_callback=None
):
    try:
        # Step 1: Create AES key and IV
        aes_key, iv = generate_session_key()

        # Step 2: Encrypt the file locally
        encrypted_file_path = "temp_encrypted_file.bin"
        encrypt_file(original_file_path, encrypted_file_path, aes_key, iv)

        # Step 3: Encrypt AES key with peer's public key
        encrypted_aes_key = encrypt_key_rsa(aes_key, peer_public_key_path)

        # Step 4: Send both AES key and file
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_ip, peer_port))

            # Send lengths first
            s.sendall(len(encrypted_aes_key).to_bytes(4, 'big'))
            s.sendall(len(iv).to_bytes(4, 'big'))

            # Send encrypted AES key and IV
            s.sendall(encrypted_aes_key)
            s.sendall(iv)

            # Send encrypted file with progress
            file_size = os.path.getsize(encrypted_file_path)
            sent = 0

            with open(encrypted_file_path, "rb") as f:
                while chunk := f.read(BUFFER_SIZE):
                    s.sendall(chunk)
                    sent += len(chunk)
                    if progress_callback:
                        progress_callback(sent, file_size)

        os.remove(encrypted_file_path)
        print("[SUCCESS] File sent successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Sending failed: {e}")
        return False


# === Function: Receive File ===
def receive_file(
    save_to_path,
    listen_port=5000,
    private_key_path="private.pem",
    progress_callback=None
):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("", listen_port))
            server.listen(1)
            print("[WAITING] Listening for incoming file...")

            conn, addr = server.accept()
            with conn:
                print(f"[CONNECTED] Connection from {addr}")

                # Read lengths
                enc_key_len = int.from_bytes(conn.recv(4), 'big')
                iv_len = int.from_bytes(conn.recv(4), 'big')

                # Receive encrypted AES key and IV
                encrypted_aes_key = conn.recv(enc_key_len)
                iv = conn.recv(iv_len)

                # Receive the encrypted file data with progress
                encrypted_data = b""
                received = 0
                estimated_total = 10 * 1024 * 1024  # fallback estimate (10 MB) if actual unknown

                while chunk := conn.recv(BUFFER_SIZE):
                    encrypted_data += chunk
                    received += len(chunk)
                    if progress_callback:
                        progress_callback(received, estimated_total)

                # Save encrypted file temporarily
                encrypted_file_path = "temp_received_encrypted_file.bin"
                with open(encrypted_file_path, "wb") as f:
                    f.write(iv + encrypted_data)

                # Decrypt AES key using our private key
                aes_key = decrypt_key_rsa(encrypted_aes_key, private_key_path)

                # Decrypt the file
                decrypt_file(encrypted_file_path, save_to_path, aes_key)
                os.remove(encrypted_file_path)

                print(f"[SUCCESS] File saved as: {save_to_path}")
                return True
    except Exception as e:
        print(f"[ERROR] Receiving failed: {e}")
        return False
