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


# --- 6. Versus the alternative -------------------------------------------
# The competitor-comparison shape, which performs because it resolves a
# decision the reader is already making. OralCheck's real competitor is not
# another site: it is googling symptoms at 1am, or asking a chatbot.
def t_versus(theme: str = "light") -> str:
    t = R.THEMES[theme]
    rows = [
        ("Asking a chatbot", "Confident answers, no idea what your mouth looks like", False),
        ("Googling symptoms", "Worst case first, every time", False),
        ("Waiting to see", "The two weeks that matter, gone", False),
        ("OralCheck", "Ten questions, then a real dentist if you need one", True),
    ]
    out = ""
    for name, note, good in rows:
        col = t["teal"] if good else t["muted"]
        bg = f"background:{t['teal']}0f;" if good else ""
        mark = "&#10003;" if good else "&#215;"
        out += f"""<div style="display:flex;gap:22px;align-items:flex-start;
             padding:26px 28px;border-radius:18px;margin-bottom:12px;{bg}">
          <span style="font-size:34px;color:{col};line-height:1;">{mark}</span>
          <div>
            <div style="font-size:32px;font-weight:600;color:{t['text']};">{name}</div>
            <div style="font-size:25px;color:{t['text_soft']};margin-top:4px;">{note}</div>
          </div>
        </div>"""
    return _frame(f"""
      {R._brandrow("01 / 07")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:66px;line-height:1.06;margin-bottom:34px;">
          What people actually do<br>about a mouth sore
        </div>
        {out}
      </div>
      <div style="font-size:25px;color:{t['muted']};">Swipe &rarr;</div>
    """, theme)


# --- 7. The number, alone ------------------------------------------------
# One figure at maximum scale. Works as a static because there is nothing to
# read: the number does the stopping.
def t_big_number(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif tnum" style="font-size:280px;line-height:0.86;color:{t['coral']};
             letter-spacing:-0.03em;">2in3</div>
        <div style="font-size:38px;line-height:1.35;color:{t['text']};margin-top:30px;max-width:780px;">
          oral cancers are found late, when treatment is hardest
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:14px;">
        <div class="footline"></div><span class="footurl">oralcheck.org</span>
      </div>
    """, theme)


# --- 8. Timeline ---------------------------------------------------------
# Turns "two weeks" from an abstract rule into something with shape.
def t_timeline(theme: str = "light") -> str:
    t = R.THEMES[theme]
    steps = [("Day 1", "You notice it", t["muted"]),
             ("Day 7", "Still there. Probably nothing.", t["muted"]),
             ("Day 14", "This is the line", t["coral"]),
             ("Day 30", "Still waiting is the risk", t["text"])]
    out = ""
    for i, (day, note, col) in enumerate(steps):
        last = i == len(steps) - 1
        out += f"""<div style="display:flex;gap:26px;">
          <div style="display:flex;flex-direction:column;align-items:center;">
            <span style="width:18px;height:18px;border-radius:50%;background:{col};"></span>
            {'' if last else f'<span style="width:3px;flex:1;background:{t["hair"]};"></span>'}
          </div>
          <div style="padding-bottom:{0 if last else 34}px;">
            <div style="font-size:22px;font-weight:700;letter-spacing:.1em;
                 text-transform:uppercase;color:{col};">{day}</div>
            <div style="font-size:32px;color:{t['text']};margin-top:6px;">{note}</div>
          </div>
        </div>"""
    return _frame(f"""
      {R._brandrow("03 / 06")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:64px;line-height:1.06;margin-bottom:40px;">
          How long is<br>too long?
        </div>
        {out}
      </div>
    """, theme)


# --- 9. Quiet question ---------------------------------------------------
# Almost empty. Stands out in a feed precisely because everything else is loud.
def t_quiet_question(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:96px;line-height:1.02;letter-spacing:-0.025em;
             color:{t['text']};">
          When did you<br>last look<br>inside your<br><span style="color:{t['coral']};">own mouth</span>?
        </div>
      </div>
      <div style="font-size:27px;color:{t['text_soft']};">Two minutes. oralcheck.org</div>
    """, theme)


# --- 10. Receipt ---------------------------------------------------------
# A deliberately plain, document-like layout. Reads as information rather
# than marketing, which is the point.
def t_receipt(theme: str = "light") -> str:
    t = R.THEMES[theme]
    lines = [("Tobacco, any form", "raises risk"), ("Heavy alcohol", "raises risk"),
             ("Both together", "multiplies it"), ("HPV exposure", "raises risk"),
             ("Sun on the lips", "raises risk"), ("Regular dental visits", "lowers it")]
    out = "".join(
        f"""<div style="display:flex;justify-content:space-between;align-items:baseline;
             padding:20px 0;border-bottom:1px dashed {t['hair']};">
          <span style="font-size:31px;color:{t['text']};">{a}</span>
          <span style="font-size:25px;color:{t['text_soft']};font-family:monospace;">{b}</span>
        </div>""" for a, b in lines)
    return _frame(f"""
      {R._brandrow("02 / 08")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div style="font-size:23px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
             color:{t['muted']};margin-bottom:8px;">What the screener weighs</div>
        <div class="serif" style="font-size:58px;line-height:1.08;margin-bottom:30px;">
          Nothing hidden
        </div>
        {out}
      </div>
      <div style="font-size:25px;color:{t['teal']};font-weight:600;">
        Full methodology at oralcheck.org/methods
      </div>
    """, theme)


TEMPLATES = [
    ("1-is-this-normal", "Is this normal?", t_is_this_normal, "light"),
    ("2-do-this-now",    "Do this now",     t_do_this_now,    "dark"),
    ("3-myth-strike",    "Myth, struck",    t_myth_strike,    "dark"),
    ("4-save-card",      "Built to be saved", t_save_card,    "light"),
    ("5-qualifier",      "The qualifier",   t_qualifier,      "dark"),
    ("6-versus",         "Versus the alternative", t_versus,  "light"),
    ("7-big-number",     "The number, alone", t_big_number,   "dark"),
    ("8-timeline",       "Timeline",        t_timeline,       "light"),
    ("9-quiet-question", "Quiet question",  t_quiet_question, "dark"),
    ("10-receipt",       "Receipt",         t_receipt,        "light"),
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    htmls = [fn(theme) for _, _, fn, theme in TEMPLATES]
    paths = R._screenshot_many(htmls)
    for (slug, _, _, _), src in zip(TEMPLATES, paths):
        dest = OUT / f"{slug}.jpg"
        dest.write_bytes(Path(src).read_bytes())
        print("wrote", dest)



# =========================================================================
# Topical templates.
#
# The Truist Park post worked because it was about something else. These are
# built to hang an oral-cancer point on a thing the reader already cares
# about: a product launch, a film, a holiday, a piece of news. Each carries a
# real image, because a topical hook without the picture of the thing is just
# a claim.
#
# ASSETS is only for these mockups. In the pipeline the image comes from the
# same photo/site-screenshot chooser the carousels already use.
# =========================================================================

ASSETS = Path(__file__).parent / "template_demo" / "assets"


def _photo(name: str, height: int, radius: int = 22, fit: str = "cover") -> str:
    p = ASSETS / name
    if not p.exists():
        p = Path(__file__).parent.parent / "public" / "self-exam" / name
    return (f"<div style=\"height:{height}px;border-radius:{radius}px;overflow:hidden;\">"
            f"<img src='{R._img_data_uri(str(p))}' "
            f"style='width:100%;height:100%;object-fit:{fit};display:block;'></div>")


# --- 11. Product verdict -------------------------------------------------
# Hangs on a launch people are already discussing, and answers the question
# honestly. The honest answer is the reason it gets shared.
def t_product_verdict(theme: str = "light") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow("01 / 06")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="kicker" style="margin-bottom:18px;">New this month</div>
        <div class="serif" style="font-size:66px;line-height:1.05;margin-bottom:26px;">
          A $300 toothbrush<br>and your cancer risk
        </div>
        {_photo("electric-toothbrush.jpg", 380)}
        <div style="display:flex;gap:16px;margin-top:26px;align-items:center;">
          <span style="background:{t['coral']};color:#fff;font-size:23px;font-weight:700;
                letter-spacing:.08em;text-transform:uppercase;padding:12px 22px;
                border-radius:100px;">Short answer: no</span>
          <span style="font-size:27px;color:{t['text_soft']};">but it is not useless either</span>
        </div>
      </div>
      <div style="font-size:25px;color:{t['muted']};">Swipe for what actually moves the needle &rarr;</div>
    """, theme)


# --- 12. Tier list -------------------------------------------------------
# A native internet format. People argue with tier lists, and arguing is
# engagement.
def t_tier_list(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    tiers = [("S", "Not smoking", t["coral"]),
             ("A", "Regular dental visits", t["teal_brt"]),
             ("B", "HPV vaccination", t["teal"]),
             ("C", "Whitening strips", t["muted"])]
    rows = "".join(
        f"""<div style="display:flex;align-items:center;gap:24px;margin-bottom:16px;">
          <span style="width:86px;height:86px;border-radius:20px;background:{c};
                color:#0d1a1b;font-family:'DM Serif Display',Georgia,serif;font-size:46px;
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">{k}</span>
          <span style="font-size:36px;color:{t['text']};">{v}</span>
        </div>""" for k, v, c in tiers)
    return _frame(f"""
      {R._brandrow("01 / 07")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:64px;line-height:1.05;margin-bottom:34px;">
          Oral health habits,<br>ranked by what<br>actually matters
        </div>
        {rows}
      </div>
      <div style="font-size:26px;color:{t['teal_brt']};font-weight:600;">
        Disagree? That is the comments section right there.
      </div>
    """, theme)


# --- 13. Calendar moment -------------------------------------------------
# The holiday hook. Timely, and the content calendar already knows the dates.
def t_calendar_moment(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow(None)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {_photo("fireworks.jpg", 440)}
        <div class="serif" style="font-size:62px;line-height:1.06;margin-top:32px;">
          Beer, sun, and the<br>two risk factors<br>nobody mentions
        </div>
        <div style="font-size:28px;line-height:1.5;color:{t['text_soft']};margin-top:20px;max-width:840px;">
          Alcohol and UV on the lips both raise oral cancer risk. The Fourth is
          not the problem. Twenty summers of it is.
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:14px;">
        <div class="footline"></div><span class="footurl">oralcheck.org</span>
      </div>
    """, theme)


# --- 14. POV card --------------------------------------------------------
# Full-bleed photo, one line over it. The most native-feeling format here.
def t_pov(theme: str = "dark") -> str:
    t = R.THEMES[theme]
    p = Path(__file__).parent.parent / "public" / "self-exam" / "cheeks-1.jpg"
    return R._doc(f"""
      <div style="width:{R.POST_W}px;height:{R.POST_H}px;position:relative;overflow:hidden;">
        <img src='{R._img_data_uri(str(p))}'
             style='position:absolute;inset:0;width:100%;height:100%;object-fit:cover;'>
        <div style="position:absolute;inset:0;background:linear-gradient(180deg,
             rgba(13,26,27,.55) 0%, rgba(13,26,27,.25) 40%, rgba(13,26,27,.93) 100%);"></div>
        <div style="position:absolute;inset:0;padding:92px 96px;display:flex;
             flex-direction:column;justify-content:space-between;">
          <div class="brandrow"><div class="brand"><div class="dot"></div>
            <span class="wordmark">OralCheck</span></div></div>
          <div>
            <div style="font-size:23px;font-weight:700;letter-spacing:.16em;
                 text-transform:uppercase;color:{t['coral']};margin-bottom:18px;">POV</div>
            <div class="serif" style="font-size:74px;line-height:1.05;color:#f2efe9;">
              you have been telling<br>yourself it is just a<br>bitten cheek for<br>three weeks
            </div>
          </div>
        </div>
      </div>""", theme)


# --- 15. In the news -----------------------------------------------------
# Reaction format. Works when a public figure is diagnosed or a study lands.
def t_in_the_news(theme: str = "light") -> str:
    t = R.THEMES[theme]
    return _frame(f"""
      {R._brandrow("01 / 05")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div style="border-left:none;background:{t['teal']}0f;border-radius:20px;padding:34px 36px;
             margin-bottom:34px;">
          <div style="font-size:22px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
               color:{t['teal']};margin-bottom:14px;">You probably saw this</div>
          <div class="serif" style="font-size:46px;line-height:1.16;color:{t['text']};">
            "Cases in men under 50 have climbed for two decades"
          </div>
        </div>
        <div class="serif" style="font-size:58px;line-height:1.08;margin-bottom:18px;">
          Here is the part<br>the headline skipped
        </div>
        <div style="font-size:30px;line-height:1.5;color:{t['text_soft']};max-width:860px;">
          The rise is real. So is the fact that most of these are found late,
          which is the part you can actually do something about.
        </div>
      </div>
      <div style="font-size:25px;color:{t['muted']};">Swipe &rarr;</div>
    """, theme)


# --- 16. Two photos, one question ----------------------------------------
# Real images side by side. The strongest teaching shape the account has.
def t_photo_compare(theme: str = "light") -> str:
    t = R.THEMES[theme]
    base = Path(__file__).parent.parent / "public"
    a = R._img_data_uri(str(base / "signs" / "sore.jpg"))
    b = R._img_data_uri(str(base / "signs" / "white.jpg"))
    def cell(src, label, col):
        return f"""<div style="flex:1;">
          <div style="height:420px;border-radius:20px;overflow:hidden;">
            <img src='{src}' style='width:100%;height:100%;object-fit:cover;display:block;'>
          </div>
          <div style="font-size:24px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
               color:{col};margin-top:18px;">{label}</div>
        </div>"""
    return _frame(f"""
      {R._brandrow("04 / 08")}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:62px;line-height:1.06;margin-bottom:30px;">
          One of these needs<br>a dentist this week
        </div>
        <div style="display:flex;gap:22px;">
          {cell(a, "Ulcer, painful", t['muted'])}
          {cell(b, "Patch, painless", t['coral'])}
        </div>
        <div style="font-size:28px;color:{t['text_soft']};margin-top:26px;">
          Painless is the one people ignore. It is also the one that matters.
        </div>
      </div>
    """, theme)


TEMPLATES += [
    ("11-product-verdict", "Product verdict",  t_product_verdict, "light"),
    ("12-tier-list",       "Tier list",        t_tier_list,       "dark"),
    ("13-calendar-moment", "Calendar moment",  t_calendar_moment, "dark"),
    ("14-pov",             "POV card",         t_pov,             "dark"),
    ("15-in-the-news",     "In the news",      t_in_the_news,     "light"),
    ("16-photo-compare",   "Two photos",       t_photo_compare,   "light"),
]

if __name__ == "__main__":
    main()
