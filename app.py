from flask import Flask, request, redirect, session
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- GOOGLE SHEET ----------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    eval(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")),
    scopes=SCOPES
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ.get("SHEET_ID")).sheet1


# ---------- STEP 1 : CLIENT NAME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client_name = request.form.get("client_name")

        if not client_name:
            return "Client name missing", 400

        session["client_name"] = client_name
        return redirect("/select")

    return """
        <h2>Enter your name</h2>
        <form method="post">
            <input name="client_name" required>
            <button type="submit">Continue</button>
        </form>
    """


# ---------- STEP 2 : PHOTO SELECTION ----------
@app.route("/select", methods=["GET", "POST"])
def select():
    client_name = session.get("client_name")

    if not client_name:
        return redirect("/")

    if request.method == "POST":
        selected = request.form.getlist("photos")
        sheet.append_row([client_name, ", ".join(selected)])
        return "Selection saved successfully"

    return "Photo selection page"
