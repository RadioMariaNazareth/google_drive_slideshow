import os
from flask import Flask, render_template, jsonify, request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
FOLDER_ID = os.environ.get("GOOGLE_FOLDER_ID")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

# --- Google Drive Logic ---
def get_drive_batch(page_token=None):
    service = build("drive", "v3", developerKey=API_KEY, cache_discovery=False)
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

# --- Routes ---
@app.route("/")
def index():
    print(">>> Serving index.html")
    return render_template("index.html")

@app.route("/api/images")
def api_images():
    print(">>> Fetching images from Google Drive")
    try:
        token = request.args.get("token")
        data = get_drive_batch(token)
        return jsonify(data)
    except Exception as e:
        print(f"[ERROR] Drive API failed: {e}")
        return jsonify({"images": [], "error": str(e)}), 500

@app.route("/api/live")
def api_live():
    print(f"\n[CHECK] Querying YouTube for: {YOUTUBE_CHANNEL_ID}")
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        search_request = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            type="video",
            eventType="live"
        )
        response = search_request.execute()
        is_live = len(response.get("items", [])) > 0
        print(f"[RESULT] Live Status: {'ONLINE' if is_live else 'OFFLINE'}")
        return jsonify({"live": is_live})
    except Exception as e:
        print(f"[ERROR] YouTube API failed: {e}")
        return jsonify({"live": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)