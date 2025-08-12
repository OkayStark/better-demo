
import os
import base64
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import time
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load .env if present
load_dotenv()

MESSAGE_FILE = "message.txt"
MESSAGES_LIST_FILE = "messages.txt"
INDEX_FILE = "message_index.txt"

DEMO_TOKEN = os.getenv("DEMO_TOKEN", "changeme")  # Set this as a secret
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this as a secret
REPO = os.getenv("GITHUB_REPO", "your-username/better-demo")  # Set this as a secret or update here

def get_messages():
    try:
        with open(MESSAGES_LIST_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return ["Welcome to Better Demo!"]

def get_current_index():
    try:
        with open(INDEX_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def get_current_message():
    messages = get_messages()
    idx = get_current_index() % len(messages)
    return messages[idx]

# Demo update endpoint
@app.route("/demo-update")
def demo_update():
    token = request.args.get("token")
    if token != DEMO_TOKEN:
        return "Unauthorized", 403

    # Rotate to next message
    messages = get_messages()
    idx = (get_current_index() + 1) % len(messages)
    new_index_content = str(idx)

    # Update message_index.txt in GitHub repo
    file_path = INDEX_FILE
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{file_path}", headers=headers)
    if r.status_code != 200:
        return f"Error fetching file: {r.text}", 500
    sha = r.json()["sha"]

    data = {
        "message": f"Demo: rotate message to index {idx} via /demo-update endpoint",
        "content": base64.b64encode(new_index_content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": "main"
    }
    r = requests.put(f"https://api.github.com/repos/{REPO}/contents/{file_path}", headers=headers, json=data)
    if r.status_code in (200, 201):
        return f"Demo update committed! Message rotated to: {messages[idx]}"
    else:
        return f"Error: {r.text}", 500

DATADOG_API_KEY = os.getenv("DATADOG_API_KEY")
SERVICE_NAME = os.getenv("SERVICE_NAME", "better-demo-app")

@app.route("/")
def index():
    message = get_current_message()
    return render_template("index.html", message=message)

@app.route("/status")
def status():
    # simple status payload with timestamp and request info
    payload = {
        "service": SERVICE_NAME,
        "status": "ok",
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "client_ip": request.remote_addr
    }

    # Basic console logging (useful for showing logs in video)
    app.logger.info("/status called: %s", payload)

    # Optional: send a lightweight event to Datadog if API key present (non-blocking)
    if DATADOG_API_KEY:
        try:
            # This is a minimal example of sending an event — not full metrics
            dd_event = {
                "title": f"{SERVICE_NAME} status called",
                "text": f"Status endpoint called at {payload['time']} from {payload['client_ip']}",
                "tags": [f"service:{SERVICE_NAME}"]
            }
            requests.post(
                f"https://api.datadoghq.com/api/v1/events?api_key={DATADOG_API_KEY}",
                json=dd_event,
                timeout=2
            )
        except Exception as e:
            app.logger.warning("Datadog event failed: %s", e)

    return jsonify(payload)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
