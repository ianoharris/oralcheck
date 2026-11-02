# Rebuilding the poster

`sections.html` and `head.html` hold the content and styles. `build.py` assembles
`../poster.html`, checks that every on-formula weight equals round(ln OR × 4.47)
and that the maximum is 61, and fails on an em dash, an exclamation mark, or a
university or reviewer name. `render.py final` writes `../poster.pdf` and
`../poster-preview.png` (needs network for Google Fonts).

    python3.11 build.py && python3.11 render.py final
