@app.route("/select")
def select():
    client_name = session.get("client_name")
    if not client_name:
        return redirect("/")

    photo_dir = os.path.join(app.static_folder, "photos")

    if not os.path.exists(photo_dir):
        return "Photos folder missing on server"

    photos = [
        f for f in os.listdir(photo_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    return render_template("viewer.html", photos=photos, client=client_name)
