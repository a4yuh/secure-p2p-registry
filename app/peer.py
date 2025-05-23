# app/peer.py

import requests

# Replace with your hosted server address (e.g., localhost or public IP)
REGISTRY_URL = "https://secure-p2p-registry.onrender.com"

def register_peer(peer_code, ip):
    print(f"🔁 Attempting to register {peer_code} → {ip}")
    try:
        response = requests.post(f"{REGISTRY_URL}/register", json={"peer_code": peer_code, "ip": ip})
        print("✅ Server response:", response.status_code, response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Registering peer failed: {e}")
        return False


def get_peer_ip(peer_code):
    try:
        response = requests.get(f"{REGISTRY_URL}/resolve/{peer_code}")
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception as e:
        print(f"[ERROR] Resolving peer failed: {e}")
    return None
