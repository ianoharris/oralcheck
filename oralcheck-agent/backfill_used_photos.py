#!/usr/bin/env python3
"""One-off: seed used_photos.json from images already posted.

The ledger was added after ~17 posts had already gone out, so those photos were
never recorded and could legitimately be picked again. Their source URLs aren't
in the manifests, but the rendered images are on disk, so we can fingerprint
them by content, which is what the dedup now matches on anyway.

Note the queue images are the final composed post (photo + text overlay), so the
perceptual hash of a raw source photo won't always match one of these. Exact and
perceptual hashes of the composed images still prevent re-posting an identical
composition, and everything generated from here on is logged at fetch time.
"""
import json
from pathlib import Path

from oralcheck_agent import USED_PHOTOS_FILE, _photo_hashes, _load_used_photos

QUEUE = Path(__file__).parent / "queue"


def main() -> None:
    used = _load_used_photos()
    before = (len(used["hashes"]), len(used["phashes"]))

    seen_files = 0
    for img in sorted(QUEUE.glob("*/*.jpg")) + sorted(QUEUE.glob("*/*.png")):
        try:
            data = img.read_bytes()
        except Exception as exc:
            print(f"skip {img.name}: {exc}")
            continue
        exact, perceptual = _photo_hashes(data)
        used["hashes"].add(exact)
        if perceptual:
            used["phashes"].add(perceptual)
        seen_files += 1

    USED_PHOTOS_FILE.write_text(json.dumps(
        {k: sorted(v) for k, v in used.items()}, indent=2))

    after = (len(used["hashes"]), len(used["phashes"]))
    print(f"scanned {seen_files} posted image(s)")
    print(f"exact hashes      {before[0]} -> {after[0]}")
    print(f"perceptual hashes {before[1]} -> {after[1]}")
    print(f"urls tracked      {len(used['urls'])}")


if __name__ == "__main__":
    main()
