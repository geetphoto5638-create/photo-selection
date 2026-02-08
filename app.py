from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)   # ← हे खूप important आहे

PHOTO_DIR = "Photos/Event1"
CLIENTS_DIR = "Clients"

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(CLIENTS_DIR, exist_ok=True)

photos = [f for f in os.listdir(PHOTO_DIR)
          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
photos.sort()

client_index = {}

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client_name = request.form.get("client_name", "").strip()
        if not client_name:
            return "Name required"

        # Client folders
        base = os.path.join(CLIENTS_DIR, client_name)
        os.makedirs(os.path.join(base, "Selected"), exist_ok=True)
        os.makedirs(os.path.join(base, "Rejected"), exist_ok=True)
        os.makedirs(os.path.join(base, "Best"), exist_ok=True)

        client_index[client_name] = 0

        if len(photos) == 0:
            return "No photos found in Photos/Event1"

        return render_template(
            "viewer.html",
            client=client_name,
            photo=photos[0]
        )

    return render_template("login.html")

@app.route('/action', methods=["POST"])
def action():
    data = request.json
    client = data['client']
    action_type = data['action']

    index = client_index.get(client, 0)
    if index >= len(photos):
        return jsonify({"done": True})

    photo = photos[index]
    target = os.path.join(CLIENTS_DIR, client, action_type)
    os.replace(
        os.path.join(PHOTO_DIR, photo),
        os.path.join(target, photo)
    )

    client_index[client] += 1
    if client_index[client] >= len(photos):
        return jsonify({"done": True})

    return jsonify({"photo": photos[client_index[client]]})

@app.route('/photos/<filename>')
def photo_file(filename):
    return send_from_directory(PHOTO_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
