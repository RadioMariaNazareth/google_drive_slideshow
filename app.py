import os
import requests
from flask import Flask, render_template, jsonify, request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
FOLDER_ID = os.environ.get("GOOGLE_FOLDER_ID")

# Use the /live URL of your channel
YOUTUBE_LIVE_URL = "https://www.youtube.com/@radiomariamnazareth/live"


# ----------------- Google Drive -----------------
def get_drive_batch(page_token=None):
    service = build(
        "drive",
        "v3",
        developerKey=API_KEY,
        cache_discovery=False
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


# ----------------- YouTube Live Detection -----------------
def is_youtube_live():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(YOUTUBE_LIVE_URL, headers=headers, timeout=5)
        html = r.text
        # Detect if any live is currently streaming
        return '"isLiveNow":true' in html
    except Exception as e:
        print("YouTube live check failed:", e)
        return False


# ----------------- Routes -----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/images")
def api_images():
    token = None
    token = request.args.get("token")
    data = get_drive_batch(token)
    return jsonify(data)


@app.route("/api/live")
def api_live():
    return jsonify({"live": is_youtube_live()})


# ----------------- Start Server -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)