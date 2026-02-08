from flask import Flask, render_template, request, jsonify
import os, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# =========================
# GOOGLE DRIVE SETUP
# =========================

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = json.loads(
    os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
)

creds = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)

# 👉 Drive folder where photos exist
DRIVE_PHOTO_FOLDER_ID = os.environ.get("DRIVE_PHOTO_FOLDER_ID")

# =========================
# MEMORY (simple & safe)
# =========================

photos = []
client_index = {}

def load_photos():
    global photos
    results = drive.files().list(
        q=f"'{DRIVE_PHOTO_FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id, name)",
        pageSize=1000
    ).execute()

    photos = results.get("files", [])
    photos.sort(key=lambda x: x["name"])

load_photos()

# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        client = request.form.get("client").strip()
        if not client:
            return "Client name required"

        if not photos:
            return "No photos found in Drive"

        client_index[client] = 0
        first = photos[0]["id"]

        return render_template(
            "viewer.html",
            client=client,
            photo_url=f"https://drive.google.com/uc?id={first}"
        )

    return render_template("login.html")


@app.route("/action", methods=["POST"])
def action():
    data = request.json
    client = data["client"]
    choice = data["action"]

    idx = client_index.get(client, 0)
    if idx >= len(photos):
        return jsonify({"done": True})

    file = photos[idx]

    # Create folder if not exists
    folder_name = f"{client}_{choice}"
    folder_id = create_folder(folder_name)

    # Move file
    drive.files().update(
        fileId=file["id"],
        addParents=folder_id,
        removeParents=DRIVE_PHOTO_FOLDER_ID,
        fields="id, parents"
    ).execute()

    client_index[client] += 1

    if client_index[client] >= len(photos):
        return jsonify({"done": True})

    next_file = photos[client_index[client]]["id"]

    return jsonify({
        "photo_url": f"https://drive.google.com/uc?id={next_file}"
    })


def create_folder(name):
    res = drive.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id)"
    ).execute()

    if res["files"]:
        return res["files"][0]["id"]

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive.files().create(body=meta, fields="id").execute()
    return folder["id"]


# =======================
