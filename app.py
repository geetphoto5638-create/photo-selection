from flask import Flask, request, render_template, redirect
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

MAIN_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------------- CLIENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client = request.form.get("client")
        return redirect(f"/viewer?client={client}")

    return '''
        <h2>Enter Client Name</h2>
        <form method="post">
            <input type="text" name="client" required>
            <button type="submit">Open Photos</button>
        </form>
    '''


# ---------------- VIEWER ----------------
@app.route("/viewer")
def viewer():
    client = request.args.get("client")

    query = f"'{MAIN_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed=false"
    results = drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    return render_template("viewer.html", files=files, client=client)


# ---------------- SAVE ----------------
@app.route("/save", methods=["POST"])
def save():
    client = request.form.get("client")
    selected_photos = request.form.getlist("photos")

    if not client:
        return "Client missing", 400

    # Check if client folder exists
    query = f"name='{client}' and '{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive.files().list(q=query, fields="files(id)").execute()
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

    # Save selected photo ids as text file
    content = "\n".join(selected_photos)

    file_metadata = {
        "name": "selection.txt",
        "parents": [client_folder_id]
    }

    media = {
        "mimeType": "text/plain"
    }

    drive.files().create(
        body=file_metadata,
        media_body=None
    ).execute()

    return "Selection Saved Successfully"


if __name__ == "__main__":
    app.run(debug=True)
