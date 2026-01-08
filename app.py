import os
from flask import Flask, render_template, jsonify, request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()  # loads .env into os.environ

app = Flask(__name__)

# ================= CONFIG =================
API_KEY = os.environ.get("GOOGLE_API_KEY")
FOLDER_ID = os.environ.get("GOOGLE_FOLDER_ID")

# ==========================================

def get_drive_batch(page_token=None):
    service = build(
        "drive",
        "v3",
        developerKey=API_KEY,
        cache_discovery=False  # IMPORTANT for Railway
    )

    query = f"'{FOLDER_ID}' in parents and mimeType contains 'image/'"

    results = service.files().list(
        q=query,
        pageSize=20,
        fields="nextPageToken, files(id, name, thumbnailLink)",
        pageToken=page_token
    ).execute()

    return {
        "images": results.get("files", []),
        "nextPageToken": results.get("nextPageToken")
    }

# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/images")
def api_images():
    token = request.args.get("token")
    data = get_drive_batch(token)
    return jsonify(data)

# ================= START ==================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
