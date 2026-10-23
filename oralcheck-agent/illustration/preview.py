"""Wrap a plate SVG in a page for screenshots: python preview.py in.svg out.html "x y w h" [show ...]
show: any of zones labels lesions (group ids made visible), or a CSS file to add."""
import sys
from pathlib import Path
svg = Path(sys.argv[1]).read_text(); vb = sys.argv[3]; show = sys.argv[4:]
w, h = (float(v) for v in vb.split()[2:])
svg = svg.replace(svg[svg.index("viewBox="):svg.index('font-family')], f'viewBox="{vb}" width="100%" height="100%" ')
css = "".join(f"#{g}{{opacity:1}}" for g in show)
font = "/Users/ianharris/projects/OralCheck/oralcheck-agent/reel3d/SourceSans3.ttf"
Path(sys.argv[2]).write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Source Sans 3'; src: url('file://{font}'); font-weight: 200 900; }}
html,body{{margin:0;height:100%;background:#f5f3f0}} svg{{display:block}} {css}</style></head><body>{svg}</body></html>""")
