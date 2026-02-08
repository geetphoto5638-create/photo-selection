from flask import Flask, render_template, request, jsonify, send_from_directory
import shutil

from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import BytesIO
import base64

app = Flask(__name__)

# ================== GOOGLE DRIVE CONFIG ==================
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive = build('drive', 'v3', credentials=creds)

EVENT_FOLDER_NAME = "Event1"
CLIENTS_FOLDER_NAME = "Clients"

# ================== HELPERS ==================
def get_folder_id(name, parent=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent:
        q += f" and '{parent}' in parents"
    res = drive.files().list(q=q).execute().get('files')
    if res:
        return res[0]['id']
    file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent:
        file_metadata['parents'] = [parent]
    return drive.files().create(body=file_metadata).execute()['id']

ROOT_ID = get_folder_id("PhotoSelection")
EVENT_ID = get_folder_id(EVENT_FOLDER_NAME, ROOT_ID)
CLIENTS_ID = get_folder_id(CLIENTS_FOLDER_NAME, ROOT_ID)

def list_photos():
    res = drive.files().list(
        q=f"'{EVENT_ID}' in parents and mimeType contains 'image/'",
        fields="files(id,name)"
    ).execute()
    return res.get('files', [])

photos = list_photos()
client_index = {}

# ================== ROUTES ==================
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("client_name")
        client_index[name] = 0
        get_folder_id(name, CLIENTS_ID)
        return render_template("viewer.html", client=name)
    return render_template("login.html")

@app.route('/photo/<client>')
def photo(client):
    i = client_index.get(client, 0)
    if i >= len(photos):
        return "DONE"
    file_id = photos[i]['id']
    data = drive.files().get_media(fileId=file_id).execute()
    img = base64.b64encode(data).decode()
    return jsonify({"image": img, "name": photos[i]['name']})

@app.route('/action', methods=["POST"])
def action():
    data = request.json
    client = data['client']
    choice = data['choice']

    i = client_index[client]
    file = photos[i]

    client_folder = get_folder_id(client, CLIENTS_ID)
    choice_folder = get_folder_id(choice, client_folder)

    drive.files().update(
        fileId=file['id'],
        addParents=choice_folder,
        removeParents=EVENT_ID
    ).execute()

    client_index[client] += 1
    return jsonify({"next": True})

# ==================
if __name__ == "__main__":
    app.run()
