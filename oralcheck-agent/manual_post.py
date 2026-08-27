#!/usr/bin/env python3
"""
Queue a hand-written post, with no model call anywhere in the path.

Every other route into the queue generates its copy first, which means the whole
pipeline stops when the Anthropic account is rate limited or out of credit, even
though rendering and posting need neither. The render layer is Playwright and
PIL only, and Telegram is plain HTTP, so a post whose copy a human already wrote
can be built and sent regardless.

Two uses: an announcement that should say something exact rather than something
generated, and any week the API is unavailable.

Edit DECK and CAPTION below, then:

    python3.11 manual_post.py
    python3.11 telegram_review.py     # sends it for approval like any other post

The deck accepts every layout in layouts.py, so this is not a degraded format.
"""
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

AGENT = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT))

import render_html as R  # noqa: E402

QUEUE = AGENT / "queue"

# Light theme: this is good news, and the warm-paper world suits it better than
# the dark editorial one.
THEME = "light"

DECK = {
    "theme": THEME,
    "kicker": "Now In Three Languages",
    "cover": {"hook": "Oral cancer does not check what language you speak."},
    "slides": [
        {
            "type": "qualifier",
            "kicker": "New",
            "headline": "OralCheck is now in English, Spanish and Portuguese",
            "emphasis": "Spanish and Portuguese",
            "body": "The same ten questions, the same two minutes, the same scoring. "
                    "Nothing is a simplified version of anything else.",
            "footnote": "oralcheck.org",
        },
        {
            "type": "versus",
            "headline": "Why a translation is not a small thing",
            "options": [
                {"name": "A health site in one language",
                 "note": "Reaches the people who already had the easiest access", "good": False},
                {"name": "An automatic browser translation",
                 "note": "Turns clinical wording into something nobody would say", "good": False},
                {"name": "OralCheck",
                 "note": "Written for each audience, checked line by line", "good": True},
            ],
            "footnote": "Swipe",
        },
        {
            "type": "checklist",
            "headline": "What is translated",
            "sub": "Not just the buttons.",
            "items": [
                "All ten screener questions",
                "Your result and what drove it",
                "The warning signs and self-exam guide",
                "The full scoring methodology",
                "Every source and citation",
            ],
            "footnote": "Nothing hidden behind English",
        },
        {
            "type": "question",
            "question": "Two minutes, in your language.",
            "emphasis": "in your language",
            "footnote": "Free. Private. oralcheck.org",
        },
    ],
    "cta": {},
}

CAPTION = (
    "OralCheck is now available in English, Spanish and Portuguese.\n\n"
    "Not a partial translation. Every screener question, every result, the warning signs, "
    "the self-exam guide, and the full scoring methodology with its sources are all "
    "translated. If you can read this in your language, you can read the evidence behind "
    "it in your language too.\n\n"
    "Oral cancer is caught late far more often than it needs to be, and language is one "
    "more reason people wait. This removes one of them.\n\n"
    "Ten questions. About two minutes. Free, private, and nothing is stored.\n\n"
    "oralcheck.org"
)

HASHTAGS = ["oralcancer", "oralhealth", "cancerawareness", "saudebucal", "saludoral"]


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    item_id = f"{stamp}_{uuid.uuid4().hex[:8]}"
    out = QUEUE / item_id
    out.mkdir(parents=True, exist_ok=True)

    print(f"Rendering {len(DECK['slides']) + 2} slides...")
    paths = R.carousel_deck(DECK, THEME)

    files = []
    for i, src in enumerate(paths, 1):
        dest = out / f"slide_{i:02d}.jpg"
        Path(src).replace(dest)
        files.append(dest.name)
        print(f"  {dest.name}")

    manifest = {
        "id": item_id,
        "media_type": "carousel",
        "hook": "OralCheck is now in English, Spanish and Portuguese",
        "caption": CAPTION,
        "hashtags": HASHTAGS,
        "files": files,
        "status": "pending",
        "pillar": "announcement",
        "theme": THEME,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nQueued {item_id} ({len(files)} slides).")
    print("Send it with:  python3.11 telegram_review.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
