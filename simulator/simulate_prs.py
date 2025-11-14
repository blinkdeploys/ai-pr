#!/usr/bin/env python3
import os
import time
import json
import requests
from threading import Thread
from flask import Flask, request

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://webhook:8000/webhook")
REPO_PATH = "/repos/test-repo"  # mounted read-only from host
app = Flask("simulator")

# Endpoint to receive posted comments (simulates GitHub)
@app.route("/receive_comment", methods=["POST"])
def receive_comment():
    payload = request.get_json()
    print("=== RECEIVED COMMENT (simulator) ===")
    print(json.dumps(payload, indent=2))
    return ("OK", 200)


def simulate_pr_events():
    # Wait for webhook to be up
    time.sleep(3)
    branches = ["feature/add-json-merge", "feature/normalize-json", "feature/json-diff-algo", "feature/json-pipeline-refactor"]
    pr_num = 1
    for br in branches:
        # prepare clone_url as absolute path inside container
        clone_url = REPO_PATH  # git clone <abs path> will clone the repo; branch selected below
        payload = {
            "action": "opened",
            "pull_request": {
                "number": pr_num,
                "head": {
                    "ref": br,
                    "repo": {
                        "clone_url": clone_url,
                        "full_name": "local/test-repo"
                    }
                }
            }
        }
        try:
            print(f"[simulator] Posting PR event for branch: {br}")
            r = requests.post(WEBHOOK_URL, json=payload, headers={"X-GitHub-Event":"pull_request"})
            print(f"[simulator] webhook returned status {r.status_code}, body: {r.text[:400]}")
        except Exception as e:
            print("Error posting webhook:", e)
        pr_num += 1
        time.sleep(1)

if __name__ == "__main__":
    # Run simulator thread to send events after flask starts
    t = Thread(target=simulate_pr_events, daemon=True)
    t.start()
    # Start flask app to receive comments from webhook
    app.run(host="0.0.0.0", port=9000)
