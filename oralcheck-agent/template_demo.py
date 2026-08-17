#!/usr/bin/env python3
"""
Mockups of candidate high-converting post templates, in OralCheck branding.

Not wired into the pipeline. This renders proposals for review; approved ones
get promoted into render_html.py as real slide layouts.

The patterns are drawn from what currently performs in health content on
Instagram: carousels out-save every other format, slide 1 decides ~80% of the
outcome, and saves/DM shares are weighted far above likes, so each template is
built to be *kept* rather than merely liked.

    python3 template_demo.py            # writes ./template_demo/*.jpg
"""
from pathlib import Path

import render_html as R

OUT = Path(__file__).parent / "template_demo"


def _frame(inner: str, theme: str) -> str:
    return R._doc(f'<div class="frame">{inner}</div>', theme)


# --- 1. Is this normal? --------------------------------------------------
# A two-panel comparison. The single most-saved shape in health content:
# people keep it to check themselves against later.
def t_is_this_normal(theme: str = "light") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow("01 / 08")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px;">
        <div class="serif" style="font-size:76px;line-height:1.05;letter-spacing:-0.015em;">
          Is this normal,<br>or worth a look?
        </div>
        <div style="display:flex;gap:20px;">
          <div style="flex:1;border:2px solid {t['hair']};border-radius:22px;padding:30px;">
            <div style="font-size:19px;font-weight:700;letter-spacing:.12em;
                 text-transform:uppercase;color:{t['teal']};margin-bottom:14px;">Usually fine</div>
            <div style="font-size:30px;line-height:1.35;color:{t['text']};">
              A sore that hurts, then fades within two weeks
            </div>
          </div>
          <div style="flex:1;border:2px solid {t['coral']};border-radius:22px;padding:30px;
               background:{t['coral']}0f;">
            <div style="font-size:19px;font-weight:700;letter-spacing:.12em;
                 text-transform:uppercase;color:{t['coral']};margin-bottom:14px;">Get it checked</div>
            <div style="font-size:30px;line-height:1.35;color:{t['text']};">
              A painless patch that is still there after two weeks
            </div>
          </div>
        </div>
      </div>
      <div style="font-size:24px;color:{t['muted']};">Swipe for the other five &rarr;</div>
    """, theme)


# --- 2. Do this now ------------------------------------------------------
# A physical action the reader can complete while holding the phone.
# Participation is what converts a scroll into a screener visit.
def t_do_this_now(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    steps = [
        ("01", "Tongue out, look at the sides"),
        ("02", "Lift it, check underneath"),
        ("03", "Pull each cheek out with a finger"),
    ]
    rows = "".join(
        f"""<div style="display:flex;gap:24px;align-items:baseline;
             padding:26px 0;border-bottom:1px solid {t['hair']};">
          <span class="serif" style="font-size:46px;color:{t['coral']};">{n}</span>
          <span style="font-size:34px;line-height:1.3;color:{t['text']};">{s}</span>
        </div>""" for n, s in steps
    )
    return _frame(f"""
      {R._brandrow("01 / 06")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="kicker" style="margin-bottom:20px;">20-second self-check</div>
        <div class="serif" style="font-size:74px;line-height:1.05;margin-bottom:16px;">
          Do this before<br>you keep scrolling
        </div>
        {rows}
      </div>
      <div style="font-size:26px;color:{t['teal_brt']};font-weight:600;">
        Found something? Save this post.
      </div>
    """, theme)


# --- 3. Myth, struck through --------------------------------------------
# The correction shape. Highly shareable because it settles an argument.
def t_myth_strike(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow("02 / 07")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:40px;">
        <div>
          <div style="font-size:19px;font-weight:700;letter-spacing:.14em;
               text-transform:uppercase;color:{t['muted']};margin-bottom:18px;">The myth</div>
          <div class="serif" style="font-size:64px;line-height:1.08;color:{t['muted']};
               text-decoration:line-through;text-decoration-color:{t['coral']};
               text-decoration-thickness:5px;">
            Only smokers get oral cancer
          </div>
        </div>
        <div style="height:2px;background:{t['hair']};"></div>
        <div>
          <div style="font-size:19px;font-weight:700;letter-spacing:.14em;
               text-transform:uppercase;color:{t['coral']};margin-bottom:18px;">Actually</div>
          <div class="serif" style="font-size:64px;line-height:1.08;color:{t['text']};">
            HPV is now the leading cause in adults under 50
          </div>
        </div>
      </div>
      <div style="font-size:26px;color:{t['teal_brt']};font-weight:600;">
        Send this to someone who thinks they are not at risk
      </div>
    """, theme)


# --- 4. Built to be saved -----------------------------------------------
# An explicit reference card. Saves are weighted far above likes, so this
# asks for the save by being genuinely worth keeping.
def t_save_card(theme: str = "light") -> str:
    t = R.THEMES[theme]
    items = ["A sore that will not heal", "A red or white patch",
             "A lump you can feel", "Numbness or trouble swallowing",
             "A rough spot on the lip"]
    rows = "".join(
        f"""<div style="display:flex;gap:18px;align-items:flex-start;margin-bottom:22px;">
          <span style="width:13px;height:13px;border-radius:50%;background:{t['coral']};
                margin-top:14px;flex-shrink:0;"></span>
          <span style="font-size:33px;line-height:1.32;">{i}</span>
        </div>""" for i in items
    )
    return _frame(f"""
      {R._brandrow("05 / 08")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:66px;line-height:1.06;margin-bottom:14px;">
          Five things worth<br>two weeks of attention
        </div>
        <div style="font-size:27px;color:{t['text_soft']};margin-bottom:40px;">
          If any of these lasts longer than that, book a check.
        </div>
        {rows}
      </div>
      <div style="display:flex;align-items:center;gap:14px;">
        <div class="footline"></div>
        <span class="footurl">Save this. It takes two weeks to matter.</span>
      </div>
    """, theme)


# --- 5. The qualifier ----------------------------------------------------
# Ad-style targeting: name the reader precisely so the right person stops.
def t_qualifier(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="kicker" style="margin-bottom:26px;">Read this if</div>
        <div class="serif" style="font-size:82px;line-height:1.04;letter-spacing:-0.02em;">
          you have had a<br>
          <span style="color:{t['coral']};">mouth sore</span><br>
          for more than<br>two weeks
        </div>
        <div style="font-size:30px;line-height:1.5;color:{t['text_soft']};margin-top:36px;max-width:820px;">
          Most are harmless. The ones that are not look exactly the same at
          this stage, which is the entire problem.
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:14px;">
        <div class="footline"></div><span class="footurl">Two-minute check at oralcheck.org</span>
      </div>
    """, theme)


TEMPLATES = [
    ("1-is-this-normal", "Is this normal?", t_is_this_normal, "light"),
    ("2-do-this-now",    "Do this now",     t_do_this_now,    "dark"),
    ("3-myth-strike",    "Myth, struck",    t_myth_strike,    "dark"),
    ("4-save-card",      "Built to be saved", t_save_card,    "light"),
    ("5-qualifier",      "The qualifier",   t_qualifier,      "dark"),
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    htmls = [fn(theme) for _, _, fn, theme in TEMPLATES]
    paths = R._screenshot_many(htmls)
    for (slug, _, _, _), src in zip(TEMPLATES, paths):
        dest = OUT / f"{slug}.jpg"
        dest.write_bytes(Path(src).read_bytes())
        print("wrote", dest)


if __name__ == "__main__":
    main()
