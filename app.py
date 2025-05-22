from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# In-memory peer registry: peer_code -> IP
peer_registry = {}

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    code = data.get("peer_code")
    ip = data.get("ip")
    if code and ip:
        peer_registry[code] = ip
        print(f"📩 Received registration: {code} → {ip}")
        return jsonify({"status": "ok"}), 200
    print("❌ Invalid registration attempt:", data)
    return jsonify({"error": "Invalid data"}), 400

@app.route("/resolve/<peer_code>", methods=["GET"])
def resolve(peer_code):
    ip = peer_registry.get(peer_code)
    if ip:
        print(f"🔎 Resolved {peer_code} → {ip}")
        return jsonify({"ip": ip})
    print(f"⚠️ Peer code {peer_code} not found.")
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Render sets this
    print(f"✅ DEBUG: Binding to 0.0.0.0 on port {port}")
    app.run(host="0.0.0.0", port=port)
