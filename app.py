from flask import Flask, render_template
import os, json

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# ---------- CREDS ----------
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

FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------- ROUTE ----------
@app.route("/")
def home():

    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'image/'",
        fields="files(id,name)"
    ).execute()

    files = results.get("files", [])

    return render_template("viewer.html", files=files, client="Test")

if __name__ == "__main__":
    app.run(debug=True)
