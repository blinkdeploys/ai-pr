import os
import json
import time
from tpyting import Dict
import httpx
from datetime import datetime


# import ai provider key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")


def execution_time(start_time):
    end_time = time.time()
    return f"{end_time - start_time} seconds"



# build reviewer prompt
def build_prompt(repo_full, pr_number, branch_path, report):
    pass


# run open ai prompt
def call_openai(prompt: str) -> str:
    pass


# generare code PR
def generate_review(repo_full, pr_number, branch, path, report):
    # start time
    start_time = time.time()
    # fetch the prompt
    prompt = build_prompt(repo_full, pr_number, branch, report)
    try:
        # run the prompt
        raw = call_openai(prompt)
        # parse the results
        parsed = json.loads(raw)
    except Exception as e:
        # fallback
        parsed = {"summary": "AI failed: " + str(e), "comments": []}
    # calculate execution time
    seconds = execution_time(start_time)
    current_time = datetime.now().strftime("%H:%M:%S")
    response = {"comment": f"**AI review**:\\n{parsed.get('summary')}",
                "structured": parsed,
                "timestamp": current_time,
                "execution_time": seconds}
    return response
