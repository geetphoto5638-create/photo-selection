from flask import Flask, request, redirect
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)   # ✅ हे खूप महत्वाचे

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

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "App is running successfully"


# ---------------- SAVE ----------------
@app.route("/save", methods=["POST"])
def save():
    try:
        client = request.form.get("client")
        photo_id = request.form.get("photo")

        if not client:
            return "Client missing", 400

        MAIN_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

        query = f"name='{client}' and '{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            client_folder_id = folders[0]["id"]
        else:
            folder_metadata = {
                "name": client,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [MAIN_FOLDER_ID]
            }
            folder = drive.files().create(body=folder_metadata, fields="id").execute()
            client_folder_id = folder.get("id")

        file_metadata = {
            "name": f"{photo_id}.txt",
            "parents": [client_folder_id]
        }

        drive.files().create(body=file_metadata).execute()

        return redirect("/")

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
