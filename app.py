import os
import json
from flask import Flask, render_template, request, redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# ---------- GOOGLE AUTH ----------
SCOPES = ["https://www.googleapis.com/auth/drive"]

service_account_info = json.loads(
    os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
)

credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)

# ---------- FOLDER IDS (CHANGE ONLY THESE) ----------
UPLOAD_FOLDER_ID = "1d9nYSYcokCa1MLxNFa6Z9Cp50LjLtsMU"
SELECTED_FOLDER_ID = "16AeNaK_0O1y0ArbT2pNo2mUtptx-7Kt3"
REJECTED_FOLDER_ID = "1xyfwKc-wGvKmCEwlDP_HgDEN_wGhyACD"

# ---------- ROUTES ----------
@app.route("/")
def index():
    results = drive_service.files().list(
        q=f"'{UPLOAD_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed=false",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])
    return render_template("index.html", files=files)


@app.route("/select/<file_id>")
def select_photo(file_id):
    drive_service.files().update(
        fileId=file_id,
        addParents=SELECTED_FOLDER_ID,
        removeParents=UPLOAD_FOLDER_ID
    ).execute()
    return redirect("/")


@app.route("/reject/<file_id>")
def reject_photo(file_id):
    drive_service.files().update(
        fileId=file_id,
        addParents=REJECTED_FOLDER_ID,
        removeParents=UPLOAD_FOLDER_ID
    ).execute()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
