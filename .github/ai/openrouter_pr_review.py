#!/usr/bin/env python3
import os, json, requests, textwrap

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
EVENT_PATH = os.environ["GITHUB_EVENT_PATH"]
MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-coder:free")
OR_KEY = os.environ["OPENROUTER_API_KEY"]
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

with open(EVENT_PATH, "r", encoding="utf-8") as f:
    event = json.load(f)
pr = event["pull_request"]["number"]

gh_hdr = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
    "X-GitHub-Api-Version": "2022-11-28",
}
diff_url = f"https://api.github.com/repos/{REPO}/pulls/{pr}"
diff = requests.get(diff_url, headers=gh_hdr, timeout=60).text

MAX = 45000
parts = [diff[i:i+MAX] for i in range(0, len(diff), MAX)] or ["(empty diff)"]

def ask_openrouter(content: str) -> str:
    sys_prompt = (
        "Ты — старший Python-ревьюер. Проект: Linux, Python 3.12. "
        "Дай краткие, но чёткие замечания по изменённым строкам: "
        "корректность, безопасность, исключения, конкуренция, утечки, сложность, стиль. "
        "Где возможно — предложи минимальные правки и патчи (unified diff). "
        "Формат: Markdown, по файлам, без воды."
    )
    payload = {
        "model": MODEL,
        "temperature": 0.2,
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Проанализируй diff PR и оставь рекомендации.\n\nDIFF:\n{content}"},
        ],
    }
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://github.com/{REPO}",
        "X-Title": "AI PR Review",
    }
    r = requests.post(OR_URL, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    js = r.json()
    return js["choices"][0]["message"]["content"]

def post_comment(body: str):
    url = f"https://api.github.com/repos/{REPO}/issues/{pr}/comments"
    hdr = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    requests.post(url, headers=hdr, json={"body": body}, timeout=60).raise_for_status()

for idx, chunk in enumerate(parts, 1):
    try:
        reply = ask_openrouter(chunk)
    except Exception as e:
        reply = f"⚠️ Ошибка обращения к OpenRouter: `{e}`"
    title = f"🤖 AI Review (часть {idx}/{len(parts)})"
    post_comment(f"### {title}\n\n{reply}")
