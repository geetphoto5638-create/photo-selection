@app.route("/save", methods=["POST"])
def save():
    try:
        client = request.form.get("client")
        photo_id = request.form.get("photo")
        status = request.form.get("status")

        if not client:
            return "Client missing", 400

        # Main PhotoSelection folder ID
        MAIN_FOLDER_ID = "1Fu10oB_TpUZxGMTmrFs5tq4lEbBd9DSa"

        # Check if client folder exists
        query = f"name='{client}' and '{MAIN_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            client_folder_id = folders[0]["id"]
        else:
            folder_metadata = {
                "name": client,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [MAIN_FOLDER_ID]
            }
            folder = drive.files().create(body=folder_metadata, fields="id").execute()
            client_folder_id = folder.get("id")

        # Create text file for selection
        file_metadata = {
            "name": f"{photo_id}.txt",
            "parents": [client_folder_id]
        }

        drive.files().create(
            body=file_metadata,
            media_body=None
        ).execute()

        return redirect(f"/view/{client}")

    except Exception as e:
        return f"Error: {str(e)}"
