import os
import json
from tpyting import Dict
import httpx


# import ai provider key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")



# build reviewer prompt
def build_prompt(repo_full, pr_number, branch_path, report):
    pass


# run open ai prompt
def call_openai(prompt: str) -> str:
    pass


# generare code PR
def generate_review(repo_full, pr_number, branch, path, report):
    pass