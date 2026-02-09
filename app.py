from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# -------- GOOGLE SHEET SETUP --------
SHEET_ID = "1WQ2YsFnxgD7UVxtn2MWFKD0dOtDaLpAqu32hEy7hj7U"

creds = Credentials.from_service_account_info(
    eval(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

# -------- ROUTES --------

@app.route("/", methods=["GET", "POST"])
def index():
    client = request.args.get("client")
    event = "event1"   # photos/event1/

    if not client:
        return "Client name missing in URL"

    photo_dir = os.path.join("photos", event)
    photos = os.listdir(photo_dir)

    return render_template(
        "viewer.html",
        photos=photos,
        client=client,
        event=event
    )


@app.route("/photos/<event>/<filename>")
def serve_photo(event, filename):
    return send_from_directory(f"photos/{event}", filename)


@app.route("/action", methods=["POST"])
def action():
    data = request.json
    sheet.append_row([
        data["client"],
        data["photo"],
        data["action"]
    ])
    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
