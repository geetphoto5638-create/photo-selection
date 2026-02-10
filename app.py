from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = "photo-selection-secret"

# ================= HOME =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        client = request.form.get("client_name")
        if not client:
            return "Client name missing"
        session["client_name"] = client
        return redirect("/select")
    return render_template("index.html")

# ================= PHOTO VIEW =================
@app.route("/select")
def select():
    client = session.get("client_name")
    if not client:
        return redirect("/")

    photo_dir = os.path.join(app.static_folder, "photos")

    if not os.path.exists(photo_dir):
        return "static/photos folder missing"

    photos = [
        f for f in os.listdir(photo_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    return render_template("viewer.html", photos=photos, client=client)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
