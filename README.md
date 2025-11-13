# AI-Assisted PR Reviewer (demo)

## Quickstart (local demo)
1. Copy files into a folder structure:
   - docker-compose.yml
   - webhook/ (Dockerfile, requirements.txt, main.py, run_checks.sh, ai_reviewer.py)
   - runner/ (optional; included in compose)
   - work/ (empty, used to mount repos)

2. Export env vars (optional)
   export GITHUB_TOKEN=ghp_xxx
   export OPENAI_API_KEY=sk-xxx

3. Build & run:
   docker compose up --build

4. To test locally without hooking to GitHub:
   - Use curl to POST a minimal simulated GitHub payload:
     curl -X POST -H "Content-Type: application/json" -H "X-GitHub-Event: pull_request" \
       --data @sample_pr_event.json http://localhost:8000/webhook

   - sample_pr_event.json should mimic GitHub's `pull_request` payload with fields: action, number, pull_request.head.repo.clone_url, pull_request.head.ref, pull_request.head.repo.full_name

This demo focuses on wiring: webhook -> run checks -> ai summary -> post comment.

## Important notes & production hardening
- **Privacy**: do not send private code to third-party APIs without approval. Consider on-prem LLMs or private endpoints.
- **Secrets**: store tokens in a secrets manager, not env vars in production.
- **Rate-limiting & safety**: throttle AI calls and sanitize diffs (redact secrets).
- **Scalability**: convert runner to a queued worker (Redis/Sidekiq) and use ephemeral containers for per-PR checks.
