from flask import Flask, render_template_string
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# ---------------- GOOGLE CREDS ----------------
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

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

# ---------------- YOUR DRIVE FOLDER ID ----------------
FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------------- ROUTE ----------------
@app.route("/")
def view():
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    html = """
    <h1>Photo Selection</h1>
    <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:10px;'>
    {% for file in files %}
        <div>
            <img src="https://drive.google.com/uc?id={{file['id']}}" width="200">
        </div>
    {% endfor %}
    </div>
    """

    return render_template_string(html, files=files)

if __name__ == "__main__":
    app.run(debug=True)
