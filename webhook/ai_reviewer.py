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
def build_prompt(repo_full: str,
                 pr_number: str,
                 branch_path: str,
                 report: str) -> str:
    # Summarize top issues and ask for suggestions

    # top issues
    top = []

    # check if security scanners like SAST, bankdit
    if report.get("bandit"):
        top.append("security findings: " + str(len(report["bandit"].get("results", []))))

    # check if linters are used
    if report.get("flake8"):
        top.append("style issues (flake8): " + str(len(report["flake8"].get("files", {}))))

    summary = "\\n".join(top) or "no automated findings"

    # prompt template
    prompt = f"""
You are an expert senior engineer reviewing a pull request for repo {repo_full} PR #{pr_number}.
Automated checks summary:
{summary}

Please produce:
1) A short 3-sentence human readable summary of the PR health.
2) A short list of suggested review comments (line-level when possible, otherwise file-level). Output JSON:
{{
 "summary": "...",
 "comments": [
   {{ "path":"path/to/file.py", "line": 123, "comment":"..."}},
   ...
 ]
}}
Only output valid JSON.
"""
    return prompt



# run open ai prompt
def call_openai(prompt: str) -> str:
    if AI_PROVIDER == "openai":
        import openai
        openai.api_key = OPENAI_KEY
        resp = openai.ChatCompletion.create(model="gpt-4o-mini", 
                                            messages=[{"role":"user","content":prompt}],
                                            max_tokens=600,
                                            temperature=0.0
                                            )
        return resp["choices"][0]["message"]["content"]
    else:
        # Fallback simple heuristic
        return json.dumps({"summary":"No AI provider configured","comments":[]})


# generare code PR
def generate_review(repo_full: str,
                    pr_number: str,
                    branch: str,
                    path: str,
                    report: str) -> Dict:
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
