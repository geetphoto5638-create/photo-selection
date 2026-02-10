from flask import Flask, render_template, request, redirect, session
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "secret123"


PHOTOS = [
    "https://picsum.photos/id/1011/300/300",
    "https://picsum.photos/id/1015/300/300",
    "https://picsum.photos/id/1025/300/300",
    "https://picsum.photos/id/1035/300/300"
]

@app.route("/select", methods=["GET", "POST"])
def select():
    client_name = session.get("client_name")

    if not client_name:
        return redirect("/")

    if request.method == "POST":
        selected = request.form.getlist("photos")
        sheet.append_row([client_name, ", ".join(selected)])
        return "Selection saved successfully"

    return render_template("viewer.html", photos=PHOTOS)
