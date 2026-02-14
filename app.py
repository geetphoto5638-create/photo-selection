from flask import Flask, render_template_string, request, redirect
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

# ---------------- MAIN FOLDER ID ----------------
MAIN_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client_name = request.form["client_name"]
        return redirect(f"/view/{client_name}")
    return """
    <h2>Enter Client Name</h2>
    <form method="POST">
        <input name="client_name" required>
        <button type="submit">Open Gallery</button>
    </form>
    """

# ---------------- VIEW PHOTOS ----------------
@app.route("/view/<client_name>")
def view(client_name):

    # Get images from main folder
    results = drive.files().list(
        q=f"'{MAIN_FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id,name)"
    ).execute()

    files = results.get("files", [])

    html = f"<h2>Client: {client_name}</h2><form method='POST' action='/save/{client_name}'>"

    for file in files:
        img_url = f"https://drive.google.com/uc?id={file['id']}"
        html += f"""
        <div style='display:inline-block;margin:10px;text-align:center;'>
            <img src="{img_url}" width="200"><br>
            <input type="checkbox" name="selected" value="{file['id']}">
        </div>
        """

    html += "<br><button type='submit'>Save Selection</button></form>"

    return html

# ---------------- SAVE SELECTION ----------------
@app.route("/save/<client_name>", methods=["POST"])
def save(client_name):

    selected_files = request.form.getlist("selected")

    # Check if client folder exists
    folders = drive.files().list(
        q=f"'{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id,name)"
    ).execute().get("files", [])

    folder_id = None

    for f in folders:
        if f["name"].lower() == client_name.lower():
            folder_id = f["id"]
            break

    # Create folder if not exists
    if not folder_id:
        folder_metadata = {
            "name": client_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [MAIN_FOLDER_ID]
        }

        folder = drive.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()

        folder_id = folder["id"]

    # Copy selected files to client folder
    for file_id in selected_files:
        drive.files().copy(
            fileId=file_id,
            body={"parents": [folder_id]}
        ).execute()

    return f"<h3>Selection Saved Successfully for {client_name}</h3>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
