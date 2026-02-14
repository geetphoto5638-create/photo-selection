from flask import Flask, render_template, request, redirect
import os
import json

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# ---------------- GOOGLE CREDS ----------------
SCOPES = ["https://www.googleapis.com/auth/drive"]

if "GOOGLE_CREDS_JSON" in os.environ:
    creds_info = json.loads(os.environ["GOOGLE_CREDS_JSON"])
else:
    with open("credentials.json", "r", encoding="utf-8") as f:
        creds_info = json.load(f)

CREDS = Credentials.from_service_account_info(
    creds_info,
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=CREDS)

# --------- MAIN PHOTO FOLDER ID ----------
PHOTO_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client = request.form["client"]
        return redirect(f"/viewer?client={client}")
    return render_template("index.html")

# ---------------- VIEWER ----------------
@app.route("/viewer")
def viewer():
    client = request.args.get("client")

    results = drive.files().list(
        q=f"'{PHOTO_FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    return render_template("viewer.html", files=files, client=client)

# ---------------- SAVE ----------------
from flask import request, redirect

@app.route("/save-multiple", methods=["POST"])
def save_multiple():

    client = request.form.get("client")
    selected = request.form.getlist("selected_photos")

    if not client:
        return "Client missing", 400

    if not selected:
        return redirect(f"/view/{client}")

    # Check if client folder exists
    folder_query = f"name='{client}' and mimeType='application/vnd.google-apps.folder'"
    folder_check = drive.files().list(q=folder_query).execute().get("files", [])

    if folder_check:
        client_folder_id = folder_check[0]["id"]
    else:
        folder_metadata = {
            "name": client,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = drive.files().create(body=folder_metadata).execute()
        client_folder_id = folder["id"]

    # Copy selected photos
    for photo_id in selected:
        drive.files().copy(
            fileId=photo_id,
            body={"parents": [client_folder_id]}
        ).execute()

    return redirect(f"/view/{client}")



# ---------------- CREATE FOLDER FUNCTION ----------------
def create_folder(name, parent_id):
    results = drive.files().list(
        q=f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if files:
        return files[0]["id"]

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = drive.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]

if __name__ == "__main__":
    app.run(debug=True)
