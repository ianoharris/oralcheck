"""Prototype 4:5 posts (1080 x 1350) from the plates.

python make_post.py plate_a.svg plate_b.svg out_dir
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from make_reel import scoped, FONT, FOOT

W, H = 1080, 1350

def post(kicker, title, body, svg, box, show, hide=()):
    css = "".join(f"#p-{g}{{opacity:1}}" for g in show) + "".join(f"#p-{g}{{opacity:0}}" for g in hide)
    s = scoped(svg, "p-").replace("preserveAspectRatio=\"xMidYMid slice\"", "preserveAspectRatio=\"xMidYMid meet\"")
    s = s.replace(s[s.index("viewBox="):s.index("width=\"100%\"")], f'viewBox="{box}" ')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Source Sans 3'; src: url('file://{FONT}'); font-weight: 200 900; }}
html,body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:#f5f3f0; font-family:'Source Sans 3',sans-serif; color:#15201f; }}
#art {{ position:absolute; left:40px; right:40px; top:230px; bottom:230px; }} #art svg {{ width:100%; height:100%; display:block; }}
#k {{ position:absolute; left:72px; top:64px; font-size:24px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:#0d7377; }}
#t {{ position:absolute; left:72px; right:72px; top:102px; font-size:52px; font-weight:600; line-height:1.08; }}
#b {{ position:absolute; left:72px; right:72px; bottom:96px; font-size:28px; line-height:1.3; color:#26393a; }}
#f {{ position:absolute; left:72px; right:72px; bottom:52px; font-size:19px; color:#5b6766; }}
#u {{ position:absolute; right:72px; top:70px; font-size:22px; font-weight:600; color:#0d7377; }}
{css}</style></head><body><div id="art">{s}</div><div id="k">{kicker}</div><div id="u">oralcheck.org</div><div id="t">{title}</div>
<div id="b">{body}</div><div id="f">{FOOT}</div></body></html>"""

if __name__ == "__main__":
    a, b, out = Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text(), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    pages = {
        "post_where.png": post("Mouth and throat", "Where mouth and throat cancers can start", "Highlighted: the tongue, the floor of the mouth, the soft palate, the tonsil and the lips. The gums, cheeks and back of the throat count too.",
                               b, "455 468 565 430", ["zones", "airway", "mouth", "labels"], ["lab-hard", "lab-epi", "lab-wall", "lab-base"]),
        "post_white_patch.png": post("What to look for", "A white patch on the side of the tongue", "A white or red patch, a sore that doesn't heal, or a lump: if it lasts more than two weeks, see a dentist or doctor.",
                                     a, "100 130 800 780", ["lesion-white", "labels"], ["lab-tonsil", "lab-cheek", "lab-gums", "lab-uvula", "lab-soft", "lab-wall", "lab-lip"]),
    }
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu"]); pg = br.new_page(viewport={"width": W, "height": H})
        for name, html in pages.items():
            f = out / (name + ".html"); f.write_text(html); pg.goto(f.as_uri()); pg.wait_for_timeout(300); pg.screenshot(path=str(out / name)); f.unlink()
        br.close()
    print(list(pages))
