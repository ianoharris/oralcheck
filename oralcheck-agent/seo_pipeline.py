#!/usr/bin/env python3
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")

CONTENT_DIR   = Path(__file__).parent.parent / "content"
KEYWORDS_FILE = Path(__file__).parent / "seo_keywords.json"
DRAFTS_DIR    = CONTENT_DIR / "drafts"
PUBLISHED_DIR = CONTENT_DIR / "published"


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


def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    fm: dict = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    return fm


def load_covered() -> list[dict]:
    """Every article the site already has (published + drafts): the 'used ideas'
    the generator must not duplicate."""
    covered = []
    for d in (PUBLISHED_DIR, DRAFTS_DIR):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            fm = _frontmatter(p.read_text())
            covered.append({
                "title": fm.get("title", ""),
                "keyword": fm.get("keyword", p.stem),
                "slug": p.stem,
            })
    return covered


def pick_next_keyword(state: dict, covered: list[dict]) -> str | None:
    """Next keyword whose topic isn't already covered by an existing article.
    Skips near-duplicates (semantic overlap judged by the model)."""
    history = state.get("history", [])
    keywords = state["keywords"]
    unused = [k for k in keywords if k not in history]
    if not unused:
        unused = keywords
        state["history"] = []

    covered_topics = [c["keyword"] for c in covered] + [c["title"] for c in covered]
    for kw in unused:
        if not _is_covered(kw, covered_topics):
            return kw
    # everything left overlaps something we've covered -> nothing new to write
    return None


def _is_covered(keyword: str, covered_topics: list[str]) -> bool:
    """Ask the model whether `keyword` is essentially the same topic as any
    already-covered article. Catches synonyms (e.g. 'symptoms' vs 'early signs')
    that a string match misses. Fails open (not covered) on error."""
    if not covered_topics:
        return False
    listing = "\n".join(f"- {t}" for t in covered_topics if t)
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY,
                     "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": "claude-sonnet-4-6", "max_tokens": 5, "temperature": 0,
                "system": "You judge whether a new blog topic substantially duplicates an existing one. Answer only YES or NO.",
                "messages": [{"role": "user", "content": (
                    f"Existing articles:\n{listing}\n\n"
                    f"New keyword: \"{keyword}\"\n\n"
                    "Would an article on the new keyword substantially duplicate the search intent "
                    "or content of any existing article above? Answer YES or NO.")}],
            }, timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip().upper().startswith("YES")
    except Exception as exc:
        print(f"dedup check failed ({exc}); treating as not covered", flush=True)
        return False


def record_keyword_used(state: dict, keyword: str) -> None:
    state["last_keyword"] = keyword
    history = state.get("history", [])
    if keyword not in history:
        history.append(keyword)
    state["history"] = history


def slugify(keyword: str) -> str:
    return keyword.lower().replace(" ", "-").replace("/", "-").replace("'", "")


def generate_article(keyword: str, covered: list[dict] | None = None) -> str:
    covered = covered or []
    if covered:
        existing = "\n".join(f'- "{c["title"]}" (targets: {c["keyword"]})' for c in covered if c["title"])
        differentiate = (
            "\n\nThe site ALREADY has these articles:\n" + existing +
            "\n\nYour article must NOT duplicate them. Do not repeat the same symptom checklist, "
            "the same structure, or the same framing they use. Take a genuinely distinct angle on "
            "this keyword (for example a different sub-topic, a how-to/self-exam angle, a specific "
            "risk group, a timeline, a myth-correction, or a decision guide), and give it a title in "
            "a DIFFERENT format from the ones above (avoid the 'X: What to Look For and When to Act' "
            "pattern if an existing article already uses it). Cross-reference rather than restate.")
    else:
        differentiate = ""

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 2000,
        "temperature": 0.7,   # variety across articles (0 made every one read the same)
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
                    f"{differentiate}\n\n"
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
    covered = load_covered()
    keyword = pick_next_keyword(state, covered)
    if not keyword:
        print("Every remaining keyword overlaps an existing article; nothing new to write.", flush=True)
        tg("OralCheck SEO: every keyword is already covered by an existing article. "
           "Add fresh keywords to seo_keywords.json.")
        return
    print(f"Generating article for: {keyword} (avoiding {len(covered)} existing)", flush=True)

    try:
        article = generate_article(keyword, covered)
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

    tg(
        f"New SEO draft ready:\n\n"
        f"{title}\n\n"
        f"Review and publish at:\n"
        f"https://oralcheck.org/review/{slug}"
    )


if __name__ == "__main__":
    main()
