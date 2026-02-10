from flask import Flask, render_template, request, redirect
import gspread, os, json, datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# ---------- Google Auth ----------
creds = Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).sheet1

drive = build("drive", "v3", credentials=creds)

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client = request.form["client"]
        return redirect(f"/view/{client}")
    return render_template("index.html")

@app.route("/view/<client>")
def view(client):
    files = drive.files().list(
        q=f"'{os.environ['DRIVE_FOLDER_ID']}' in parents and mimeType contains 'image/'",
        fields="files(id,name)"
    ).execute()["files"]

    return render_template("viewer.html", files=files, client=client)

@app.route("/save", methods=["POST"])
def save():
    sheet.append_row([
        request.form["client"],
        request.form["photo"],
        request.form["status"],
        str(datetime.datetime.now())
    ])
    return "OK"
