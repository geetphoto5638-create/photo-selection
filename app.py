from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

PHOTO_FOLDER = "static/photos"
CLIENT_FOLDER = "clients"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client_name = request.form.get("client_name")

        if not client_name:
            return "Client name missing", 400

        path = os.path.join(CLIENT_FOLDER, client_name)
        os.makedirs(path, exist_ok=True)

        open(os.path.join(path, "selected.txt"), "a").close()
        open(os.path.join(path, "rejected.txt"), "a").close()

        return redirect(url_for("viewer", client=client_name))

    return render_template("index.html")


@app.route("/viewer")
def viewer():
    client = request.args.get("client")
    if not client:
        return "Client missing", 400

    photos = os.listdir(PHOTO_FOLDER)
    return render_template("viewer.html", photos=photos, client=client)


@app.route("/action", methods=["POST"])
def action():
    client = request.form.get("client")
    photo = request.form.get("photo")
    decision = request.form.get("decision")

    client_path = os.path.join(CLIENT_FOLDER, client)

    file = "selected.txt" if decision == "select" else "rejected.txt"

    with open(os.path.join(client_path, file), "a") as f:
        f.write(photo + "\n")

    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
