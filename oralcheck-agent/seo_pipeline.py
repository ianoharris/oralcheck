#!/usr/bin/env python3
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN    = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID  = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS_FILE = Path(__file__).parent / "seo_keywords.json"
DRAFTS_DIR    = Path(__file__).parent.parent / "content" / "drafts"


def tg(text: str) -> None:
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=15,
        )
    except Exception:
        pass


def load_keywords() -> dict:
    return json.loads(KEYWORDS_FILE.read_text())


def save_keywords(state: dict) -> None:
    KEYWORDS_FILE.write_text(json.dumps(state, indent=2))


def pick_next_keyword(state: dict) -> str:
    history = state.get("history", [])
    keywords = state["keywords"]
    # Reset rotation when all have been used
    unused = [k for k in keywords if k not in history]
    if not unused:
        unused = keywords
        state["history"] = []
    return unused[0]


def record_keyword_used(state: dict, keyword: str) -> None:
    state["last_keyword"] = keyword
    history = state.get("history", [])
    if keyword not in history:
        history.append(keyword)
    state["history"] = history


def slugify(keyword: str) -> str:
    return keyword.lower().replace(" ", "-").replace("/", "-").replace("'", "")


def generate_article(keyword: str) -> str:
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 2000,
        "temperature": 0,
        "system": (
            "You are a medical content writer for OralCheck (oralcheck.org), "
            "a free oral cancer risk screener. Write evidence-based, accurate content. "
            "Brand voice: direct, calm, never alarmist. No em dashes. No exclamation marks. "
            "Always recommend professional medical consultation."
        ),
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Write a 900-1100 word SEO blog article targeting the keyword: \"{keyword}\"\n\n"
                    "Structure:\n"
                    "- H1 title that naturally includes the keyword\n"
                    "- Intro paragraph: hook + why this matters\n"
                    "- 3-4 H2 sections with substantive content\n"
                    "- Conclusion with a soft CTA to take the free screener at oralcheck.org\n"
                    "- Medical disclaimer at the bottom\n\n"
                    "Output valid markdown only. No preamble."
                ),
            }
        ],
    }

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def extract_title(article: str) -> str:
    for line in article.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def main() -> None:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    state = load_keywords()
    keyword = pick_next_keyword(state)
    print(f"Generating article for: {keyword}", flush=True)

    try:
        article = generate_article(keyword)
    except Exception as exc:
        tg(f"OralCheck SEO pipeline error: Claude API failed for '{keyword}'\n{exc}")
        sys.exit(1)

    title = extract_title(article)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    slug  = slugify(keyword)
    filename = f"{today}-{slug}.md"

    frontmatter = (
        f"---\n"
        f'title: "{title}"\n'
        f'date: "{today}"\n'
        f'keyword: "{keyword}"\n'
        f'status: "draft"\n'
        f"---\n\n"
    )

    (DRAFTS_DIR / filename).write_text(frontmatter + article)
    print(f"Saved: content/drafts/{filename}", flush=True)

    record_keyword_used(state, keyword)
    save_keywords(state)

    preview = article[:200].replace("\n", " ").strip()
    tg(
        f"OralCheck SEO draft ready for review\n\n"
        f"Keyword: {keyword}\n"
        f"Title: {title}\n"
        f"File: content/drafts/{filename}\n\n"
        f"Preview: {preview}..."
    )


if __name__ == "__main__":
    main()
