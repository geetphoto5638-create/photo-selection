from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# ---------------- CONFIG ----------------
PHOTO_DIR = "Photos/Event1"
CLIENTS_DIR = "Clients"
DATA_FILE = "clients.json"

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(CLIENTS_DIR, exist_ok=True)

# ----------------------------------------

def load_clients():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_clients(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

clients = load_clients()

def get_photos():
    photos = [f for f in os.listdir(PHOTO_DIR)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    photos.sort()
    return photos

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client = request.form.get("client_name", "").strip()
        if not client:
            return "Client name required"

        now = datetime.now()

        # first time client → create validity (7 days example)
        if client not in clients:
            expiry = now + timedelta(days=7)
            clients[client] = {
                "index": 0,
                "expiry": expiry.isoformat()
            }

            base = os.path.join(CLIENTS_DIR, client)
            os.makedirs(os.path.join(base, "Selected"), exist_ok=True)
            os.makedirs(os.path.join(base, "Rejected"), exist_ok=True)
            os.makedirs(os.path.join(base, "Best"), exist_ok=True)

            save_clients(clients)

        # expiry check
        expiry = datetime.fromisoformat(clients[client]["expiry"])
        if now > expiry:
            return "❌ Link expired. Please contact studio."

        photos = get_photos()
        if not photos:
            return "No photos found"

        idx = clients[client]["index"]
        if idx >= len(photos):
            return "✅ Selection completed"

        return render_template(
            "viewer.html",
            client=client,
            photo=photos[idx]
        )

    return render_template("login.html")

# ---------------- ACTION ----------------
@app.route("/action", methods=["POST"])
def action():
    data = request.json
    client = data["client"]
    action_type = data["action"]

    clients = load_clients()
    photos = get_photos()

    if client not in clients:
        return jsonify({"error": "Invalid client"})

    idx = clients[client]["index"]
    if idx >= len(photos):
        return jsonify({"done": True})

    photo = photos[idx]
    target = os.path.join(CLIENTS_DIR, client, action_type)

    os.replace(
        os.path.join(PHOTO_DIR, photo),
        os.path.join(target, photo)
    )

    clients[client]["index"] += 1
    save_clients(clients)

    photos = get_photos()
    if clients[client]["index"] >= len(photos):
        return jsonify({"done": True})

    return jsonify({"photo": photos[clients[client]["index"]]})

# ---------------- PHOTOS ----------------
@app.route("/photos/<filename>")
def photo_file(filename):
    return send_from_directory(PHOTO_DIR, filename)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
