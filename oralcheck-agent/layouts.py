"""
The post templates, as real layouts the generator can select.

These were designed and approved in `template_demo.py`, but that file renders
fixed copy for review and nothing imports it. The pipeline meanwhile only ever
had five generic shapes (cover / stat / fact / list / quote), so every carousel
came out looking the same no matter how good the idea was. This module is the
missing half: the same sixteen designs, parameterised, and wired into
`render_deck` so a slide spec can actually ask for one.

Two things differ from the demos, both forced by the content being real:

* **Type scales with the copy.** The demos were hand-set around fixed strings.
  Generated copy varies wildly in length, and a headline tuned for six words
  overflows at fourteen. `_fit` shrinks the size as the string grows, so a long
  headline gets smaller instead of getting cut off.
* **Every field degrades.** A layout given half its fields renders the half it
  has rather than emitting an empty box. Layouts needing a photo return None
  when there isn't one, and the caller falls back to a typographic slide.

Adding a layout: write the function, add it to `LAYOUTS`, and describe it in
`SLIDE_SPEC` in oralcheck_agent.py. It is unreachable until it is in both.
"""
from __future__ import annotations

from pathlib import Path

import render_html as R

_e = R._e


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------

def _fit(text: str, base: int, ideal: int, floor: float = 0.55) -> int:
    """Font size for `text` at `base`px, assuming `ideal` characters fit there.

    Long strings scale down, short ones never scale up past base (oversized type
    on a short line looks like a mistake, not a decision). The square root keeps
    the falloff gentle: a string twice as long lands at ~70% rather than 50%,
    which is what actually fits given the text also gains lines as it shrinks.
    """
    n = len(text or "")
    if n <= ideal:
        return base
    scale = max(floor, (ideal / n) ** 0.5)
    return int(base * scale)


def _lines(text: str) -> str:
    """Honour deliberate line breaks in generated copy, escaping the rest."""
    return "<br>".join(_e(p) for p in str(text or "").split("\n"))


def _frame(inner: str, theme: str) -> str:
    return R._doc(f'<div class="frame">{inner}</div>', theme)


def _photo_box(path: str | None, height: int, radius: int = 22) -> str:
    if not path or not Path(path).exists():
        return ""
    return (f"<div style=\"height:{height}px;border-radius:{radius}px;overflow:hidden;\">"
            f"<img src='{R._img_data_uri(str(path))}' "
            f"style='width:100%;height:100%;object-fit:cover;display:block;'></div>")


def _footnote(text: str, t: dict, color: str | None = None) -> str:
    if not text:
        return ""
    return (f"<div style=\"font-size:25px;color:{color or t['muted']};font-weight:600;\">"
            f"{_e(text)}</div>")


def _footrule(text: str, t: dict) -> str:
    if not text:
        return ""
    return ("<div style='display:flex;align-items:center;gap:14px;'>"
            f"<div class='footline'></div><span class='footurl'>{_e(text)}</span></div>")


# ---------------------------------------------------------------------------
# 1. Compare - two panels, "usually fine" vs "get it checked"
# ---------------------------------------------------------------------------
# The most-saved shape in health content: people keep it to check themselves
# against later.

def l_compare(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    panels = ""
    for i, key in enumerate(("a", "b")):
        label = s.get(f"{key}_label", "")
        text = s.get(f"{key}_text", "")
        if not text:
            continue
        alarm = i == 1
        border = t["coral"] if alarm else t["hair"]
        bg = f"background:{t['coral']}0f;" if alarm else ""
        col = t["coral"] if alarm else t["teal"]
        panels += f"""
          <div style="flex:1;border:2px solid {border};border-radius:22px;padding:30px;{bg}">
            <div style="font-size:19px;font-weight:700;letter-spacing:.12em;
                 text-transform:uppercase;color:{col};margin-bottom:14px;">{_e(label)}</div>
            <div style="font-size:{_fit(text, 30, 52)}px;line-height:1.35;color:{t['text']};">
              {_lines(text)}</div>
          </div>"""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px;">
        <div class="serif" style="font-size:{_fit(head, 76, 30)}px;line-height:1.05;
             letter-spacing:-0.015em;">{_lines(head)}</div>
        <div style="display:flex;gap:20px;">{panels}</div>
      </div>
      {_footnote(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 2. Steps - a physical action the reader can finish while holding the phone
# ---------------------------------------------------------------------------

def l_steps(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    steps = [x for x in s.get("steps", []) if str(x).strip()][:4]
    rows = "".join(
        f"""<div style="display:flex;gap:24px;align-items:baseline;
             padding:24px 0;border-bottom:1px solid {t['hair']};">
          <span class="serif tnum" style="font-size:46px;color:{t['coral']};">{i:02d}</span>
          <span style="font-size:{_fit(str(step), 34, 40)}px;line-height:1.3;
                color:{t['text']};">{_e(step)}</span>
        </div>""" for i, step in enumerate(steps, 1))
    kicker = s.get("kicker", "")
    kicker_html = f"<div class='kicker' style='margin-bottom:20px;'>{_e(kicker)}</div>" if kicker else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="serif" style="font-size:{_fit(head, 74, 28)}px;line-height:1.05;
             margin-bottom:16px;">{_lines(head)}</div>
        {rows}
      </div>
      {_footnote(s.get("footnote", ""), t, t["teal_brt"])}
    """, theme)


# ---------------------------------------------------------------------------
# 3. Myth - the correction shape. Shareable because it settles an argument.
# ---------------------------------------------------------------------------

def l_myth(s: dict, t: dict, theme: str, counter: str | None) -> str:
    myth, truth = s.get("myth", ""), s.get("truth", "")
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:40px;">
        <div>
          <div style="font-size:19px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
               color:{t['muted']};margin-bottom:18px;">The myth</div>
          <div class="serif" style="font-size:{_fit(myth, 64, 34)}px;line-height:1.08;
               color:{t['muted']};text-decoration:line-through;
               text-decoration-color:{t['coral']};text-decoration-thickness:5px;">
            {_lines(myth)}</div>
        </div>
        <div style="height:2px;background:{t['hair']};"></div>
        <div>
          <div style="font-size:19px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
               color:{t['coral']};margin-bottom:18px;">Actually</div>
          <div class="serif" style="font-size:{_fit(truth, 64, 34)}px;line-height:1.08;
               color:{t['text']};">{_lines(truth)}</div>
        </div>
      </div>
      {_footnote(s.get("footnote", ""), t, t["teal_brt"])}
    """, theme)


# ---------------------------------------------------------------------------
# 4. Checklist - an explicit reference card, built to be worth keeping
# ---------------------------------------------------------------------------

def l_checklist(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    sub = s.get("sub", "")
    items = [str(i).strip() for i in s.get("items", []) if str(i).strip()][:6]
    size = 33 if len(items) <= 5 else 29
    rows = "".join(
        f"""<div style="display:flex;gap:18px;align-items:flex-start;margin-bottom:22px;">
          <span style="width:13px;height:13px;border-radius:50%;background:{t['coral']};
                margin-top:14px;flex-shrink:0;"></span>
          <span style="font-size:{_fit(i, size, 42)}px;line-height:1.32;">{_e(i)}</span>
        </div>""" for i in items)
    sub_html = (f"<div style='font-size:27px;color:{t['text_soft']};margin-bottom:40px;'>"
                f"{_e(sub)}</div>") if sub else "<div style='height:26px;'></div>"
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(head, 66, 32)}px;line-height:1.06;
             margin-bottom:14px;">{_lines(head)}</div>
        {sub_html}
        {rows}
      </div>
      {_footrule(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 5. Qualifier - name the reader precisely so the right person stops
# ---------------------------------------------------------------------------

def l_qualifier(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    emph = s.get("emphasis", "")
    # The emphasised phrase is coloured in place, so the headline still reads as
    # one sentence rather than a headline with a caption bolted on.
    marked = _lines(head)
    if emph and _e(emph) in marked:
        marked = marked.replace(_e(emph), f"<span style='color:{t['coral']}'>{_e(emph)}</span>", 1)
    body = s.get("body", "")
    body_html = (f"<div style='font-size:30px;line-height:1.5;color:{t['text_soft']};"
                 f"margin-top:36px;max-width:820px;'>{_lines(body)}</div>") if body else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="kicker" style="margin-bottom:26px;">{_e(s.get("kicker", "Read this if"))}</div>
        <div class="serif" style="font-size:{_fit(head, 82, 40)}px;line-height:1.04;
             letter-spacing:-0.02em;">{marked}</div>
        {body_html}
      </div>
      {_footrule(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 6. Versus - the competitor comparison
# ---------------------------------------------------------------------------
# OralCheck's real competitor is not another site. It is googling symptoms at
# 1am, or asking a chatbot, or waiting. Naming those is the whole point.

def l_versus(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    rows = ""
    for opt in s.get("options", [])[:4]:
        if not isinstance(opt, dict) or not opt.get("name"):
            continue
        good = bool(opt.get("good"))
        col = t["teal"] if good else t["muted"]
        bg = f"background:{t['teal']}0f;" if good else ""
        mark = "&#10003;" if good else "&#215;"
        note = opt.get("note", "")
        note_html = (f"<div style='font-size:25px;color:{t['text_soft']};margin-top:4px;'>"
                     f"{_e(note)}</div>") if note else ""
        rows += f"""<div style="display:flex;gap:22px;align-items:flex-start;
             padding:26px 28px;border-radius:18px;margin-bottom:12px;{bg}">
          <span style="font-size:34px;color:{col};line-height:1;">{mark}</span>
          <div><div style="font-size:32px;font-weight:600;color:{t['text']};">{_e(opt['name'])}</div>
          {note_html}</div>
        </div>"""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(head, 66, 34)}px;line-height:1.06;
             margin-bottom:34px;">{_lines(head)}</div>
        {rows}
      </div>
      {_footnote(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 7. Big number - one figure at maximum scale
# ---------------------------------------------------------------------------

def l_bignumber(s: dict, t: dict, theme: str, counter: str | None) -> str:
    value = str(s.get("value", ""))
    label = s.get("label", "")
    # 280px suits three or four glyphs. "2in3" and "1 in 10" are very different
    # widths, so the scale comes off the actual string.
    size = 280 if len(value) <= 4 else (210 if len(value) <= 7 else 150)
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif tnum" style="font-size:{size}px;line-height:0.86;color:{t['coral']};
             letter-spacing:-0.03em;">{_e(value)}</div>
        <div style="font-size:{_fit(label, 38, 60)}px;line-height:1.35;color:{t['text']};
             margin-top:30px;max-width:820px;">{_lines(label)}</div>
      </div>
      {_footrule(s.get("footnote", "oralcheck.org"), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 8. Timeline - turns an abstract rule into something with shape
# ---------------------------------------------------------------------------

def l_timeline(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    steps = [x for x in s.get("steps", []) if isinstance(x, dict) and x.get("label")][:4]
    rows = ""
    for i, step in enumerate(steps):
        last = i == len(steps) - 1
        # The marked step is the decision point; the last is where the risk sits.
        col = t["coral"] if step.get("mark") else (t["text"] if last else t["muted"])
        rows += f"""<div style="display:flex;gap:26px;">
          <div style="display:flex;flex-direction:column;align-items:center;">
            <span style="width:18px;height:18px;border-radius:50%;background:{col};"></span>
            {'' if last else f'<span style="width:3px;flex:1;background:{t["hair"]};"></span>'}
          </div>
          <div style="padding-bottom:{0 if last else 34}px;">
            <div style="font-size:22px;font-weight:700;letter-spacing:.1em;
                 text-transform:uppercase;color:{col};">{_e(step['label'])}</div>
            <div style="font-size:{_fit(step.get('note', ''), 32, 34)}px;color:{t['text']};
                 margin-top:6px;">{_e(step.get('note', ''))}</div>
          </div>
        </div>"""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(head, 64, 26)}px;line-height:1.06;
             margin-bottom:40px;">{_lines(head)}</div>
        {rows}
      </div>
      {_footnote(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 9. Question - almost empty, which is why it stops a feed
# ---------------------------------------------------------------------------

def l_question(s: dict, t: dict, theme: str, counter: str | None) -> str:
    q = s.get("question", "")
    emph = s.get("emphasis", "")
    marked = _lines(q)
    if emph and _e(emph) in marked:
        marked = marked.replace(_e(emph), f"<span style='color:{t['coral']}'>{_e(emph)}</span>", 1)
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(q, 96, 38)}px;line-height:1.02;
             letter-spacing:-0.025em;color:{t['text']};">{marked}</div>
      </div>
      <div style="font-size:27px;color:{t['text_soft']};">
        {_e(s.get("footnote", "Two minutes. oralcheck.org"))}</div>
    """, theme)


# ---------------------------------------------------------------------------
# 10. Receipt - deliberately document-like. Reads as information, not marketing.
# ---------------------------------------------------------------------------

def l_receipt(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    rows = ""
    for row in s.get("rows", [])[:7]:
        if isinstance(row, dict):
            a, b = row.get("label", ""), row.get("value", "")
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            a, b = row[0], row[1]
        else:
            continue
        if not a:
            continue
        rows += f"""<div style="display:flex;justify-content:space-between;align-items:baseline;
             gap:24px;padding:20px 0;border-bottom:1px dashed {t['hair']};">
          <span style="font-size:31px;color:{t['text']};">{_e(a)}</span>
          <span style="font-size:25px;color:{t['text_soft']};font-family:monospace;
                text-align:right;flex-shrink:0;">{_e(b)}</span>
        </div>"""
    kicker = s.get("kicker", "")
    kicker_html = (f"<div style='font-size:23px;font-weight:700;letter-spacing:.16em;"
                   f"text-transform:uppercase;color:{t['muted']};margin-bottom:8px;'>"
                   f"{_e(kicker)}</div>") if kicker else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="serif" style="font-size:{_fit(head, 58, 24)}px;line-height:1.08;
             margin-bottom:30px;">{_lines(head)}</div>
        {rows}
      </div>
      {_footnote(s.get("footnote", ""), t, t["teal"])}
    """, theme)


# ---------------------------------------------------------------------------
# 11. Verdict - hangs on a launch people are already discussing
# ---------------------------------------------------------------------------
# The honest answer is the reason it gets shared, so the badge is allowed to
# say no.

def l_verdict(s: dict, t: dict, theme: str, counter: str | None) -> str | None:
    photo = _photo_box(s.get("photo"), 380)
    if not photo:
        return None
    head = s.get("headline", "")
    verdict = s.get("verdict", "")
    note = s.get("verdict_note", "")
    badge = (f"<span style=\"background:{t['coral']};color:#fff;font-size:23px;font-weight:700;"
             f"letter-spacing:.08em;text-transform:uppercase;padding:12px 22px;"
             f"border-radius:100px;\">{_e(verdict)}</span>") if verdict else ""
    note_html = (f"<span style='font-size:27px;color:{t['text_soft']};'>{_e(note)}</span>"
                 if note else "")
    kicker = s.get("kicker", "")
    kicker_html = f"<div class='kicker' style='margin-bottom:18px;'>{_e(kicker)}</div>" if kicker else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {kicker_html}
        <div class="serif" style="font-size:{_fit(head, 66, 30)}px;line-height:1.05;
             margin-bottom:26px;">{_lines(head)}</div>
        {photo}
        <div style="display:flex;gap:16px;margin-top:26px;align-items:center;">
          {badge}{note_html}</div>
      </div>
      {_footnote(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 12. Tier list - a native internet format. People argue with tier lists.
# ---------------------------------------------------------------------------

def l_tier(s: dict, t: dict, theme: str, counter: str | None) -> str:
    head = s.get("headline", "")
    colors = [t["coral"], t["teal_brt"], t["teal"], t["muted"], t["hair"]]
    rows = ""
    for i, tier in enumerate(s.get("tiers", [])[:5]):
        if not isinstance(tier, dict) or not tier.get("label"):
            continue
        rank = str(tier.get("rank", "S"))[:2]
        rows += f"""<div style="display:flex;align-items:center;gap:24px;margin-bottom:16px;">
          <span style="width:86px;height:86px;border-radius:20px;background:{colors[i % len(colors)]};
                color:{t['bg']};font-family:'DM Serif Display',Georgia,serif;font-size:46px;
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">{_e(rank)}</span>
          <span style="font-size:{_fit(tier['label'], 36, 30)}px;color:{t['text']};">
            {_e(tier['label'])}</span>
        </div>"""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(head, 64, 34)}px;line-height:1.05;
             margin-bottom:34px;">{_lines(head)}</div>
        {rows}
      </div>
      {_footnote(s.get("footnote", ""), t, t["teal_brt"])}
    """, theme)


# ---------------------------------------------------------------------------
# 13. Moment - the calendar/holiday hook
# ---------------------------------------------------------------------------

def l_moment(s: dict, t: dict, theme: str, counter: str | None) -> str | None:
    photo = _photo_box(s.get("photo"), 440)
    if not photo:
        return None
    head = s.get("headline", "")
    body = s.get("body", "")
    body_html = (f"<div style='font-size:28px;line-height:1.5;color:{t['text_soft']};"
                 f"margin-top:20px;max-width:840px;'>{_lines(body)}</div>") if body else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {photo}
        <div class="serif" style="font-size:{_fit(head, 62, 34)}px;line-height:1.06;
             margin-top:32px;">{_lines(head)}</div>
        {body_html}
      </div>
      {_footrule(s.get("footnote", "oralcheck.org"), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 14. POV - full-bleed photo, one line over it. The most native format here.
# ---------------------------------------------------------------------------

def l_pov(s: dict, t: dict, theme: str, counter: str | None) -> str | None:
    path = s.get("photo")
    if not path or not Path(str(path)).exists():
        return None
    line = s.get("line", "")
    return R._doc(f"""
      <div style="width:{R.POST_W}px;height:{R.POST_H}px;position:relative;overflow:hidden;">
        <img src='{R._img_data_uri(str(path))}'
             style='position:absolute;inset:0;width:100%;height:100%;object-fit:cover;'>
        <div style="position:absolute;inset:0;background:linear-gradient(180deg,
             rgba(13,26,27,.55) 0%, rgba(13,26,27,.25) 40%, rgba(13,26,27,.93) 100%);"></div>
        <div style="position:absolute;inset:0;padding:92px 96px;display:flex;
             flex-direction:column;justify-content:space-between;">
          <div class="brandrow"><div class="brand"><div class="dot"></div>
            <span class="wordmark">OralCheck</span></div></div>
          <div>
            <div style="font-size:23px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
                 color:{t['coral']};margin-bottom:18px;">{_e(s.get("kicker", "POV"))}</div>
            <div class="serif" style="font-size:{_fit(line, 74, 60)}px;line-height:1.05;
                 color:#f2efe9;">{_lines(line)}</div>
          </div>
        </div>
      </div>""", theme)


# ---------------------------------------------------------------------------
# 15. News - the reaction format, for when a study or headline lands
# ---------------------------------------------------------------------------

def l_news(s: dict, t: dict, theme: str, counter: str | None) -> str:
    quote = s.get("quote", "")
    head = s.get("headline", "")
    body = s.get("body", "")
    quote_html = (f"""<div style="background:{t['teal']}0f;border-radius:20px;padding:34px 36px;
           margin-bottom:34px;">
        <div style="font-size:22px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
             color:{t['teal']};margin-bottom:14px;">{_e(s.get("quote_kicker", "You probably saw this"))}</div>
        <div class="serif" style="font-size:{_fit(quote, 46, 60)}px;line-height:1.16;
             color:{t['text']};">&ldquo;{_lines(quote)}&rdquo;</div>
      </div>""") if quote else ""
    body_html = (f"<div style='font-size:30px;line-height:1.5;color:{t['text_soft']};"
                 f"max-width:860px;'>{_lines(body)}</div>") if body else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        {quote_html}
        <div class="serif" style="font-size:{_fit(head, 58, 30)}px;line-height:1.08;
             margin-bottom:18px;">{_lines(head)}</div>
        {body_html}
      </div>
      {_footnote(s.get("footnote", ""), t)}
    """, theme)


# ---------------------------------------------------------------------------
# 16. Photo compare - two real images. The strongest teaching shape here.
# ---------------------------------------------------------------------------

def l_photocompare(s: dict, t: dict, theme: str, counter: str | None) -> str | None:
    a, b = s.get("a_photo"), s.get("b_photo")
    if not (a and b and Path(str(a)).exists() and Path(str(b)).exists()):
        return None

    def cell(src: str, label: str, col: str) -> str:
        return f"""<div style="flex:1;min-width:0;">
          <div style="height:420px;border-radius:20px;overflow:hidden;">
            <img src='{R._img_data_uri(str(src))}'
                 style='width:100%;height:100%;object-fit:cover;display:block;'>
          </div>
          <div style="font-size:24px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
               color:{col};margin-top:18px;">{_e(label)}</div>
        </div>"""

    head = s.get("headline", "")
    note = s.get("note", "")
    note_html = (f"<div style='font-size:28px;color:{t['text_soft']};margin-top:26px;'>"
                 f"{_lines(note)}</div>") if note else ""
    return _frame(f"""
      {R._brandrow(counter)}
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div class="serif" style="font-size:{_fit(head, 62, 30)}px;line-height:1.06;
             margin-bottom:30px;">{_lines(head)}</div>
        <div style="display:flex;gap:22px;">
          {cell(a, s.get("a_label", ""), t["muted"])}
          {cell(b, s.get("b_label", ""), t["coral"])}
        </div>
        {note_html}
      </div>
    """, theme)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

LAYOUTS = {
    "compare": l_compare,
    "steps": l_steps,
    "myth": l_myth,
    "checklist": l_checklist,
    "qualifier": l_qualifier,
    "versus": l_versus,
    "bignumber": l_bignumber,
    "timeline": l_timeline,
    "question": l_question,
    "receipt": l_receipt,
    "verdict": l_verdict,
    "tier": l_tier,
    "moment": l_moment,
    "pov": l_pov,
    "news": l_news,
    "photocompare": l_photocompare,
}

# Layouts that cannot render without an image. The deck builder only offers
# these when it actually has one, and render() still returns None as a backstop.
PHOTO_LAYOUTS = {"verdict", "moment", "pov", "photocompare"}

# Layouts that work as a standalone single-image post: they carry a whole idea
# on one slide rather than depending on the swipe before or after.
STANDALONE_LAYOUTS = ("question", "bignumber", "qualifier", "myth", "tier",
                      "compare", "receipt", "pov")


def render(slide: dict, theme: str = "dark", counter: str | None = None) -> str | None:
    """Render one templated slide, or None if this layout cannot be built."""
    fn = LAYOUTS.get(str(slide.get("type", "")).lower().strip())
    if not fn:
        return None
    t = R.THEMES.get(theme, R.THEMES["dark"])
    try:
        return fn(slide, t, theme, counter)
    except Exception:  # noqa: BLE001
        # A malformed slide spec must not take down a whole carousel. Callers
        # fall back to a plain typographic slide.
        return None
