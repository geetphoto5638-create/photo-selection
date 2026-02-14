from flask import Flask, request, render_template_string
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# ---------------- GOOGLE CREDS ----------------
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

creds_info = json.loads(os.environ["GOOGLE_CREDS_JSON"])
CREDS = Credentials.from_service_account_info(
    creds_info,
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=CREDS)

# ---------------- MAIN FOLDER ID ----------------
MAIN_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

# ---------------- HOME PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client_name = request.form["client"]
        return view_client(client_name)

    return """
    <h2>Enter Client Name</h2>
    <form method="POST">
        <input type="text" name="client" required>
        <button type="submit">View Photos</button>
    </form>
    """

# ---------------- VIEW CLIENT ----------------
def view_client(client_name):

    # Find client folder inside main folder
    folder = drive.files().list(
        q=f"name='{client_name}' and '{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not folder:
        return "Client folder not found"

    folder_id = folder[0]["id"]

    # Get images
    files = drive.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    html = """
    <h1>Photos for {{client}}</h1>
    <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:10px;'>
    {% for file in files %}
        <div>
            <img src="https://drive.google.com/uc?id={{file['id']}}" width="200">
        </div>
    {% endfor %}
    </div>
    """

    return render_template_string(html, files=files, client=client_name)

if __name__ == "__main__":
    app.run(debug=True)
