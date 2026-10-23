# Illustration prototypes (23 Oct 2026)

Textbook-style mouth and throat plates for posts, reels and, later, the Learn pages.
Why this exists, and what it replaces: `docs/MODEL_REVIEW.md`.

- **Plate A** (`build_plate_a.py`): the open mouth from the front, with switchable lesions.
- **Plate B** (`build_plate_b.py`): a side cut-away with the head as a faded silhouette, with switchable "where it starts" zones.

Outlines are traced from the Z-Anatomy head model in `../anatomy3d/head.glb` (main checkout), so
proportions come from the atlas; the parts the atlas gets wrong or lacks are redrawn by hand in the
builders, each marked in a comment.

```
../.venv-stats/bin/python3.11 build_all.py OUT_DIR [--no-video]
```

rebuilds both plates (SVG), the two 4:5 posts, the nine lesion crops (seven on plate A, two on plate B), `lesions.py` draws them, and the two 12-second reels
(illustration and 3D, same captions). Steps: `render_plate.py` draws flat masks and id maps from the
model (`shots/*.json`), `tracer.py` turns them into smooth outlines, the two builders style them,
`make_post.py` and `make_reel.py` lay out posts and reels, `reel3d_frames.py` renders the 3D comparison.
`src/plate.js` is the renderer (bundle with `node build.mjs`).

**Licence.** Traced from Z-Anatomy (CC BY-SA 4.0), built on BodyParts3D (CC BY-SA 2.1 JP), so every
output is an adaptation and is shared under CC BY-SA 4.0. Captions carry:
"Illustration based on Z-Anatomy (CC BY-SA 4.0) and BodyParts3D (CC BY-SA 2.1 JP). Shared under CC BY-SA 4.0."

**Medical framing.** Lesion drawings are matched to published photos, not reviewed by a clinician.
Every frame says "Illustration for education, not a real case. Not reviewed by a clinician." Keep it.
