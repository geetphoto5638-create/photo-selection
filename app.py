from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = "secret123"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        if not client_name:
            return "Client name missing"

        session["client_name"] = client_name
        return redirect("/select")

    return render_template("index.html")


@app.route("/select", methods=["GET"])
def select():
    client_name = session.get("client_name")
    if not client_name:
        return redirect("/")

    photos = os.listdir("static/photos")
    return render_template("viewer.html", photos=photos)


if __name__ == "__main__":
    app.run(debug=True)
