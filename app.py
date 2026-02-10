from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

PHOTO_FOLDER = "static/photos"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        if not client_name:
            return "Client name missing", 400
        return redirect(url_for("viewer", client=client_name))
    return render_template("index.html")

@app.route("/viewer")
def viewer():
    client = request.args.get("client")
    if not client:
        return "Client name missing", 400

    if not os.path.exists(PHOTO_FOLDER):
        return "static/photos folder missing", 500

    photos = [
        f for f in os.listdir(PHOTO_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    return render_template("viewer.html", photos=photos, client=client)

if __name__ == "__main__":
    app.run(debug=True)
