#!/usr/bin/env python3
"""One-off: translate every currently-published English article into Spanish
and save it under content/published/es/<same filename>. Going forward, new
articles get their Spanish version generated automatically by seo_pipeline.py
at draft time (see translate_article_to_spanish there) — this script only
backfills the articles that existed before that wiring landed.
"""
from pathlib import Path
from seo_pipeline import PUBLISHED_DIR, PUBLISHED_ES_DIR, translate_article_to_spanish, extract_title

def main():
    PUBLISHED_ES_DIR.mkdir(parents=True, exist_ok=True)
    articles = sorted(PUBLISHED_DIR.glob("*.md"))
    for path in articles:
        es_path = PUBLISHED_ES_DIR / path.name
        if es_path.exists():
            print(f"skip (already translated): {path.name}")
            continue
        text = path.read_text()
        # split frontmatter from body
        if not text.startswith("---"):
            print(f"skip (no frontmatter): {path.name}")
            continue
        end = text.index("---", 3)
        frontmatter, body = text[: end + 3], text[end + 3:].lstrip("\n")
        # pull title/keyword out of frontmatter for the translation prompt
        fm_lines = frontmatter.strip("-\n").splitlines()
        fm = {}
        for line in fm_lines:
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        title = fm.get("title", path.stem)
        keyword = fm.get("keyword", title)
        print(f"translating: {path.name} ({title})")
        es_body = translate_article_to_spanish(body, title, keyword)
        es_title = extract_title(es_body)
        es_frontmatter = frontmatter.replace(f'title: "{title}"', f'title: "{es_title}"')
        es_path.write_text(es_frontmatter + "\n\n" + es_body)
        print(f"  -> saved content/published/es/{path.name}")

if __name__ == "__main__":
    main()
