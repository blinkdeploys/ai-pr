import os
import json
import tempfile
import subprocess
from fastapi import FastAPI, Request, Header, HTTPException
import httpx
from pathlib import Path
from ai_reviewer import generate_review

app = FastAPI()
WORK_DIR = Path("/work")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")



@app.post("/webhook")
async def webhook(req: Request, x_github_event: str = Header(None)):
    # webhook that usess a normalized version of the checker
    pass



@app.post("/webhook_sh")
async def webhook_sh(req: Request, x_github_event: str = Header(None)):
    # uses the sh script for running checkers
    # run checks (runner script)
    runner_script = Path("/app/run_checks.sh")

    payload = await req.json()
    # Only handle pull_request events here
    if x_github_event != "pull_request":
        return {"ok": True, "msg": f"event {x_github_event} ignored"}

    action = payload.get("action")
    if action not in ("opened", "synchronize", "reopened"):
        return {"ok": True, "msg": f"action {action} ignored"}

    pr = payload.get("pull_request", {})
    clone_url = pr.get("head", {}).get("repo", {}).get("clone_url")
    branch = pr.get("head", {}).get("ref")
    number = pr.get("number")
    repo_full = pr.get("head", {}).get("repo", {}).get("full_name")

    if not clone_url or not branch:
        raise HTTPException(status_code=400, detail="missing clone info")

    tmpdir = WORK_DIR / f"{repo_full.replace('/', '_')}_pr{number}"
    if tmpdir.exists():
        # remove or fetch; for simplicity remove
        subprocess.run(["rm", "-rf", str(tmpdir)], check=False)
    tmpdir.mkdir(parents=True, exist_ok=True)
    # correct temp path
    report_path = tmpdir / "pr_report.json"

    # Clone only the PR branch (shallow)
    clone_cmd = ["git", "clone", "--depth", "1", "--branch", branch, clone_url, str(tmpdir)]
    proc = subprocess.run(clone_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr}

    # call runner container via mounted volume approach: run local script that uses installed tools
    # For simplicity, run a local script included here
    run_proc = subprocess.run(["/app/run_checks.sh", str(tmpdir), str(report_path)], capture_output=True, text=True)
    if run_proc.returncode != 0:
        # still continue — we want AI to summarize failures
        pass

    if not report_path.exists():
        return {"ok": False, "error": "report not generated", "stdout": run_proc.stdout, "stderr": run_proc.stderr}

    report = json.loads(report_path.read_text())

    # create AI review
    ai_response = generate_review(repo_full, number, branch, tmpdir, report)

    # post as PR comment using GitHub API
    comment = {
        "body": ai_response.get("comment", "AI review produced no comment")
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    # uses remote git repo : to build out local repo for contained testing
    gh_url = f"https://api.github.com/repos/{repo_full}/issues/{number}/comments"

    async with httpx.AsyncClient() as client:
        r = await client.post(gh_url, headers=headers, json=comment)
        if r.status_code >= 400:
            return {"ok": False, "gh_error": r.text}

    return {"ok": True, "ai": ai_response}
