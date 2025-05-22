# app/peer.py

import requests

# Replace with your hosted server address (e.g., localhost or public IP)
REGISTRY_URL = "http://localhost:5001"

def register_peer(peer_code, ip):
    try:
        response = requests.post(f"{REGISTRY_URL}/register", json={"peer_code": peer_code, "ip": ip})
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
