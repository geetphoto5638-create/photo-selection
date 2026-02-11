from flask import Flask, render_template, request, redirect, url_for
import os

import json, os
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])

CREDS = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)



app = Flask(__name__)

# ================= GOOGLE DRIVE =================

SCOPES = ["https://www.googleapis.com/auth/drive"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDS = Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "credentials.json"),
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=CREDS)

# 🔴 इथे तुमचा Drive Folder ID टाका
PARENT_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"


# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("client")
        return redirect(url_for("view", client=name))
    return render_template("index.html")


@app.route("/view/<client>")
def view(client):

    # 🔹 Images fetch
    results = drive.files().list(
        q=f"'{PARENT_FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id,name)"
    ).execute()

    files = results.get("files", [])

    return render_template("viewer.html", files=files, client=client)


@app.route("/save", methods=["POST"])
def save():
    client = request.form["client"]
    selected = request.form.getlist("photos")

    # 🔹 Create client folder
    folder_metadata = {
        "name": client,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [PARENT_FOLDER_ID]
    }

    folder = drive.files().create(body=folder_metadata).execute()
    client_folder_id = folder["id"]

    # 🔹 Copy selected photos
    for file_id in selected:
        drive.files().copy(
            fileId=file_id,
            body={"parents": [client_folder_id]}
        ).execute()

    # 🔹 Save text file
    content = "\n".join(selected)

    drive.files().create(
        body={
            "name": "selected.txt",
            "parents": [client_folder_id]
        },
        media_body=content
    ).execute()

    return "Selection Saved Successfully ✅"


if __name__ == "__main__":
    app.run(debug=True)
