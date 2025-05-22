# app/encryption.py

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import hashes

# === AES-256 Session Key Generation ===
def generate_session_key():
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)   # 128-bit IV
    return key, iv

# === AES File Encryption ===
def encrypt_file(input_file, output_file, key, iv):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    with open(input_file, 'rb') as f:
        data = f.read()

    padded_data = padder.update(data) + padder.finalize()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_file, 'wb') as f:
        f.write(iv + encrypted)  # Prepend IV for decryption

# === AES File Decryption ===
def decrypt_file(encrypted_file, output_file, key):
    with open(encrypted_file, 'rb') as f:
        iv = f.read(16)
        encrypted_data = f.read()

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    with open(output_file, 'wb') as f:
        f.write(decrypted)

# === RSA Keypair Generation ===
def generate_rsa_keys(private_key_path="private.pem", public_key_path="public.pem"):
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# === RSA Encrypt AES Key ===
def encrypt_key_rsa(aes_key, peer_public_key_path):
    with open(peer_public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

    encrypted_key = public_key.encrypt(
        aes_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key

# === RSA Decrypt AES Key ===
def decrypt_key_rsa(encrypted_key, private_key_path):
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    aes_key = private_key.decrypt(
        encrypted_key,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_key
