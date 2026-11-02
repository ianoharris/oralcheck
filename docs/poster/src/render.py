import sys, json
from playwright.sync_api import sync_playwright
import os
HERE = os.path.dirname(os.path.abspath(__file__))
html = os.path.join(HERE, "..", "poster.html")
out = sys.argv[1] if len(sys.argv) > 1 else "measure"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 4608, "height": 3456})
    pg.goto("file://" + html)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    info = pg.evaluate("""() => {
      const r = {};
      r.main = document.querySelector('main').getBoundingClientRect().toJSON();
      r.cols = [...document.querySelectorAll('.col')].map(c => ({h: c.scrollHeight, ch: c.clientHeight, w: c.clientWidth,
         secs: [...c.children].map(s => [s.querySelector('h2,h3')?.textContent.slice(0,20), Math.round(s.getBoundingClientRect().height)])}));
      r.fonts = [...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family+' '+f.weight);
      return r; }""")
    print(json.dumps(info, indent=1))
    if out == "final":
        pg.screenshot(path=os.path.join(HERE, "..", "poster-preview.png"), full_page=False)
        pg.emulate_media(media="print")
        pg.pdf(path=os.path.join(HERE, "..", "poster.pdf"), width="48in", height="36in", print_background=True,
               margin={"top":"0","bottom":"0","left":"0","right":"0"})
    else:
        pg.screenshot(path=out + ".png")
    b.close()
