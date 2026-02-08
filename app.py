from flask import Flask, render_template, request, redirect, url_for
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)

# ---------------------------
# CONFIG
# ---------------------------
TEMP_DIR = "static/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Google Drive setup (replace with your credentials)
# Make sure `drive_service` is properly authenticated
drive_service = build('drive', 'v3', credentials=YOUR_CREDENTIALS)

# Example: list of file IDs from Drive
photos_list = [
    {"id": "file_id_1", "name": "photo1.jpg"},
    {"id": "file_id_2", "name": "photo2.jpg"},
    # add more
]
current_index = 0

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def download_photo(file_id, filename):
    """Download photo from Google Drive to TEMP_DIR"""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(TEMP_DIR, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()

def get_next_photo():
    """Return next photo filename"""
    global current_index
    if current_index >= len(photos_list):
        return None
    photo = photos_list[current_index]
    download_photo(photo['id'], photo['name'])
    return photo['name']

def move_photo_to_folder(file_id, folder_id):
    """Move file in Drive (on Select / Reject)"""
    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents='root',  # adjust according to your folder structure
        fields='id, parents'
    ).execute()

# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def index():
    photo = get_next_photo()
    if not photo:
        return "No more photos!"
    return render_template("viewer.html", photo=photo)

@app.route("/action", methods=["POST"])
def action():
    global current_index
    action_type = request.form.get("action")  # select or reject
    if current_index >= len(photos_list):
        return redirect(url_for('index'))
    
    photo = photos_list[current_index]
    file_id = photo['id']
    
    # Example: folder IDs for Select/Reject
    if action_type == "select":
        move_photo_to_folder(file_id, folder_id="SELECT_FOLDER_ID")
    elif action_type == "reject":
        move_photo_to_folder(file_id, folder_id="REJECT_FOLDER_ID")
    
    # Increment index
    current_index += 1
    return redirect(url_for('index'))

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
