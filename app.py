import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# =========================
# GOOGLE DRIVE CONFIG
# =========================
SCOPES = ["https://www.googleapis.com/auth/drive"]

service_account_info = json.loads(
    os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
)

creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=creds)

# =========================
# DRIVE FUNCTIONS
# =========================
def create_drive_folder(folder_name, parent_id=None):
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]

    folder = drive_service.files().create(
        body=file_metadata,
        fields="id"
    ).execute()

    return folder.get("id")


def upload_to_drive(file_path, filename, folder_id):
    media = MediaFileUpload(file_path, resumable=True)
    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }

    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()


# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client_name = request.form.get("client_name")

        if not client_name:
            return "Client name required", 400

        # Create client folder
        client_folder_id = create_drive_folder(client_name)

        # Create subfolders
        create_drive_folder("Selected", client_folder_id)
        create_drive_folder("Rejected", client_folder_id)

        return redirect(url_for("upload", client=client_name, folder_id=client_folder_id))

    return render_template("login.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    client = request.args.get("client")
    folder_id = request.args.get("folder_id")

    if request.method == "POST":
        files = request.files.getlist("photos")

        for file in files:
            save_path = os.path.join("/tmp", file.filename)
            file.save(save_path)
            upload_to_drive(save_path, file.filename, folder_id)

        return "Photos uploaded successfully!"

    return render_template("viewer.html", client=client)


@app.route("/action", methods=["POST"])
def action():
    data = request.json
    return jsonify({"status": "saved", "data": data})


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
