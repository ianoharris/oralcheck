#!/usr/bin/env python3
import csv
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN    = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID  = os.environ["TELEGRAM_CHAT_ID"]

CONTACTS_FILE = Path(__file__).parent.parent / "outreach-contacts.csv"
DRAFTS_DIR    = Path(__file__).parent.parent / "outreach-drafts"

FOLLOWUP_PROMPT = """\
You are drafting a follow-up email for Ian Harris at OralCheck (oralcheck.org).

Contact: {name} at {organization} ({email})
Original outreach date: {date_emailed}
Context/notes: {notes}

OralCheck is a free, private oral cancer risk screener, 10 questions, 2 minutes. Ian is a predental biology student at UW-Madison reaching out to dental schools, cancer organizations, and health advocacy groups about potential partnerships, patient education use, or research collaboration.

Write a short, warm follow-up email (3-4 sentences max). Opening: "Hi {first_name}," not "Dear". No em dashes. No hollow phrases like "I hope this finds you well." Be specific to the context/notes if provided. End with "Thanks," then Ian's signature block.

Signature:
Ian Harris
Biology B.S. (Junior) | Global Health Minor
University of Wisconsin-Madison
(561) 465-6508 | ioharris@wisc.edu

Output the email body only (no subject line).\
"""


def tg(text: str) -> None:
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=15,
        )
    except Exception:
        pass


def load_contacts() -> list[dict]:
    if not CONTACTS_FILE.exists():
        return []
    with open(CONTACTS_FILE, newline="") as f:
        return list(csv.DictReader(f))


def needs_followup(row: dict) -> bool:
    if row.get("Status", "").strip() != "Pending":
        return False
    try:
        contacted = datetime.strptime(row["Date_Emailed"].strip(), "%Y-%m-%d").date()
    except (KeyError, ValueError):
        return False
    return (date.today() - contacted) >= timedelta(days=7)


def first_name(name: str) -> str:
    parts = name.strip().split()
    return parts[-1] if parts[0] == "Dr." else parts[0]


def generate_draft(row: dict) -> str:
    prompt = FOLLOWUP_PROMPT.format(
        name=row["Name"].strip(),
        organization=row["Organization"].strip(),
        email=row["Email"].strip(),
        date_emailed=row["Date_Emailed"].strip(),
        notes=row.get("Notes", "").strip() or "No additional context.",
        first_name=first_name(row["Name"]),
    )

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


def save_draft(row: dict, body: str) -> None:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    safe_name = row["Name"].replace(" ", "-").replace(".", "")
    safe_org  = row["Organization"].replace("/", "-").replace(" ", "-")
    filename  = f"{today}-{safe_name}-{safe_org}.md"

    content = (
        f'---\n'
        f'to: "{row["Email"].strip()}"\n'
        f'name: "{row["Name"].strip()}"\n'
        f'organization: "{row["Organization"].strip()}"\n'
        f'date_drafted: "{today}"\n'
        f'original_contact: "{row["Date_Emailed"].strip()}"\n'
        f'---\n\n'
        f'Subject: Following up -- OralCheck\n\n'
        f'{body}\n'
    )
    (DRAFTS_DIR / filename).write_text(content)


def main() -> None:
    if not CONTACTS_FILE.exists():
        tg("Outreach tracker: outreach-contacts.csv not found in repo root. Add it to get started.")
        sys.exit(0)

    contacts = load_contacts()
    due = [r for r in contacts if needs_followup(r)]

    if not due:
        tg("No follow-ups needed this week.")
        sys.exit(0)

    drafted = []
    for row in due:
        try:
            body = generate_draft(row)
            save_draft(row, body)
            drafted.append(f"- {row['Name']} -- {row['Organization']}")
        except Exception as exc:
            print(f"Failed for {row.get('Name')}: {exc}", flush=True)

    if not drafted:
        tg("Outreach follow-ups due but all drafts failed. Check Actions logs.")
        sys.exit(1)

    tg(
        f"Outreach follow-ups drafted ({len(drafted)}):\n\n"
        + "\n".join(drafted)
        + "\n\nReview at: oralcheck/outreach-drafts/"
    )


if __name__ == "__main__":
    main()
