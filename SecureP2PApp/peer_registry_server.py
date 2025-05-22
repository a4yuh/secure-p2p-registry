# peer_registry_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

peer_registry = {}

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    code = data.get("peer_code")
    ip = data.get("ip")
    if code and ip:
        peer_registry[code] = ip
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route("/resolve/<peer_code>", methods=["GET"])
def resolve(peer_code):
    ip = peer_registry.get(peer_code)
    if ip:
        return jsonify({"ip": ip})
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("✅ DEBUG: Binding to 0.0.0.0 on port", port)
    app.run(host="0.0.0.0", port=port)