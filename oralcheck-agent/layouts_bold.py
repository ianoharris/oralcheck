"""A second visual family for posts: bold, full-colour slides.

The original layouts (render_html.py, layouts.py) all share one look: a cream
or dark page, a serif headline and a short accent rule. Ian found that every
carousel and image looked the same (22 Oct 2026), so this family is built
differently: whole slides in brand colour, oversized letters and numerals,
rounded cards and pill tags. It starts with the two formats he picked, quiz
carousels and a weekly series.

Every function returns a complete HTML document at POST_W x POST_H, rendered
by render_html._screenshot_many like the others.
"""
import html as _html

import render_html as R

INK, TEAL, TEAL_BRT, CORAL = "#0d1a1b", "#0d7377", "#14a8ae", "#e8634a"
CREAM, SAND, SOFT = "#f4f1ea", "#e8e4de", "#5a7476"
W, H = R.POST_W, R.POST_H
LETTER_COLOURS = {"A": CORAL, "B": TEAL, "C": INK, "D": TEAL_BRT}


def _e(t) -> str:
    return _html.escape(str(t))


def _doc(body: str, bg: str) -> str:
    dm, ss = R._font_b64("DMSerifDisplay-Regular.ttf"), R._font_b64("SourceSans3-Regular.ttf")
    css = f"""
@font-face {{ font-family: 'DM Serif Display'; src: url('data:font/truetype;base64,{dm}') format('truetype'); font-display: block; }}
@font-face {{ font-family: 'Source Sans 3'; src: url('data:font/truetype;base64,{ss}') format('truetype'); font-weight: 300 700; font-display: block; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {W}px; height: {H}px; }}
body {{ background: {bg}; overflow: hidden; position: relative; font-family: 'Source Sans 3', system-ui, sans-serif;
       -webkit-font-smoothing: antialiased; }}
.serif {{ font-family: 'DM Serif Display', Georgia, serif; font-weight: 400; }}
.pill {{ display: inline-flex; align-items: center; height: 54px; padding: 0 26px; border-radius: 27px;
        font-size: 24px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}
.chip {{ display: inline-flex; align-items: center; height: 58px; padding: 0 28px; border-radius: 29px;
        font-size: 27px; font-weight: 600; }}
.mark {{ position: absolute; left: 84px; top: 76px; display: flex; align-items: center; gap: 12px;
        font-size: 22px; font-weight: 700; letter-spacing: 0.06em; }}
.mark i {{ width: 12px; height: 12px; border-radius: 50%; background: {CORAL}; display: block; }}
.count {{ position: absolute; right: 84px; top: 78px; font-size: 22px; font-weight: 700; letter-spacing: 0.08em; }}
"""
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"


def _mark(colour: str, counter: str | None) -> str:
    c = f"<div class='count' style='color:{colour};opacity:0.7'>{_e(counter)}</div>" if counter else ""
    return f"<div class='mark' style='color:{colour}'><i></i>OralCheck</div>{c}"


def _letter(ch: str, size: int, bg: str, fg: str) -> str:
    return (f"<div class='serif' style='width:{size}px;height:{size}px;border-radius:50%;background:{bg};color:{fg};"
            f"display:flex;align-items:center;justify-content:center;font-size:{int(size * 0.6)}px;line-height:1;"
            f"padding-bottom:{int(size * 0.06)}px'>{_e(ch)}</div>")


# --- quiz -----------------------------------------------------------------------

def quiz_cover(title: str, sub: str, number: int, letters=("A", "B", "C"), counter: str | None = None) -> str:
    circles = "".join(_letter(ch, 128, CREAM, INK) for ch in letters)
    body = f"""
    {_mark(INK, counter)}
    <div class='serif' style='position:absolute;right:-60px;top:120px;font-size:1150px;line-height:1;color:{CREAM};opacity:0.16'>?</div>
    <div style='position:absolute;left:84px;top:250px;right:84px'>
      <div class='pill' style='border:3px solid {INK};color:{INK}'>Quiz &middot; {number:02d}</div>
      <div class='serif' style='font-size:112px;line-height:1.0;color:{INK};margin-top:54px;letter-spacing:-0.01em'>{_e(title)}</div>
      <div style='font-size:38px;line-height:1.35;color:{INK};opacity:0.82;margin-top:34px;max-width:820px;font-weight:600'>{_e(sub)}</div>
    </div>
    <div style='position:absolute;left:84px;bottom:96px;display:flex;align-items:center;gap:22px'>
      {circles}
      <div style='font-size:30px;font-weight:700;color:{INK};margin-left:18px'>Guess, then swipe &rarr;</div>
    </div>"""
    return _doc(body, CORAL)


def quiz_option(ch: str, headline: str, chips: list[str], body_text: str, counter: str | None = None) -> str:
    col = LETTER_COLOURS.get(ch, TEAL)
    chips_html = "".join(f"<span class='chip' style='background:{SAND};color:{INK}'>{_e(c)}</span>" for c in chips)
    body = f"""
    {_mark(TEAL, counter)}
    <div class='serif' style='position:absolute;right:-40px;bottom:-230px;font-size:980px;line-height:1;color:{col};opacity:0.07'>{_e(ch)}</div>
    <div style='position:absolute;left:84px;top:300px;right:84px'>
      {_letter(ch, 230, col, CREAM)}
      <div class='serif' style='font-size:84px;line-height:1.04;color:{INK};margin-top:58px;letter-spacing:-0.01em'>{_e(headline)}</div>
      <div style='display:flex;flex-wrap:wrap;gap:16px;margin-top:44px'>{chips_html}</div>
      <div style='font-size:33px;line-height:1.5;color:{SOFT};margin-top:44px;max-width:860px'>{_e(body_text)}</div>
    </div>
    <div style='position:absolute;left:84px;bottom:84px;font-size:27px;font-weight:700;color:{TEAL}'>Is this the one? Keep your guess &rarr;</div>"""
    return _doc(body, CREAM)


def quiz_reveal(ch: str, headline: str, body_text: str, counter: str | None = None) -> str:
    body = f"""
    {_mark(CREAM, counter)}
    <div style='position:absolute;left:84px;top:210px'>
      <div class='pill' style='background:{TEAL_BRT};color:{INK}'>The answer</div>
    </div>
    <div style='position:absolute;left:60px;top:250px;display:flex;align-items:flex-end;gap:10px'>
      <div class='serif' style='font-size:560px;line-height:1;color:{CORAL}'>{_e(ch)}</div>
      <div style='width:150px;height:150px;border-radius:50%;background:{TEAL_BRT};margin-bottom:110px;display:flex;
           align-items:center;justify-content:center'>
        <svg width='76' height='76' viewBox='0 0 24 24'><path d='M4 12.5l5 5L20 6.5' fill='none' stroke='{INK}'
             stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'/></svg></div>
    </div>
    <div style='position:absolute;left:84px;right:84px;top:850px'>
      <div class='serif' style='font-size:74px;line-height:1.06;color:{CREAM}'>{_e(headline)}</div>
      <div style='font-size:33px;line-height:1.5;color:#b8cfd1;margin-top:30px;max-width:880px'>{_e(body_text)}</div>
    </div>"""
    return _doc(body, INK)


def quiz_recap(title: str, rows: list[tuple[str, str, str, bool]], counter: str | None = None) -> str:
    """rows: (letter, what it was, verdict, is_the_answer)"""
    cards = ""
    for ch, what, verdict, hit in rows:
        col = LETTER_COLOURS.get(ch, TEAL)
        pill = (f"<span class='pill' style='background:{CORAL};color:{CREAM}'>{_e(verdict)}</span>" if hit else
                f"<span class='pill' style='background:{SAND};color:{INK}'>{_e(verdict)}</span>")
        cards += f"""
        <div style='display:flex;align-items:center;gap:34px;background:#ffffff;border-radius:34px;padding:34px 38px;
             box-shadow:0 2px 0 rgba(13,26,27,0.06){";outline:4px solid " + CORAL if hit else ""}'>
          {_letter(ch, 112, col, CREAM)}
          <div style='flex:1'>
            <div class='serif' style='font-size:46px;line-height:1.1;color:{INK}'>{_e(what)}</div>
            <div style='margin-top:16px'>{pill}</div>
          </div>
        </div>"""
    body = f"""
    {_mark(TEAL, counter)}
    <div style='position:absolute;left:84px;right:84px;top:200px'>
      <div class='serif' style='font-size:80px;line-height:1.04;color:{INK}'>{_e(title)}</div>
      <div style='display:flex;flex-direction:column;gap:26px;margin-top:56px'>{cards}</div>
    </div>"""
    return _doc(body, CREAM)


def quiz_end(question: str, line: str, url: str = "oralcheck.org", counter: str | None = None) -> str:
    body = f"""
    {_mark(INK, counter)}
    <div style='position:absolute;left:84px;right:84px;top:300px'>
      <div class='serif' style='font-size:116px;line-height:1.0;color:{INK}'>{_e(question)}</div>
      <div style='font-size:38px;line-height:1.4;color:{INK};opacity:0.85;margin-top:40px;font-weight:600;max-width:820px'>{_e(line)}</div>
    </div>
    <div style='position:absolute;left:84px;right:84px;bottom:96px;display:flex;align-items:flex-end;justify-content:space-between'>
      <div>
        <div style='font-size:26px;font-weight:700;color:{INK};opacity:0.7;letter-spacing:0.04em'>Check your own risk, free</div>
        <div style='font-size:52px;font-weight:700;color:{INK};margin-top:6px'>{_e(url)}</div>
      </div>
      <div class='pill' style='background:{INK};color:{CREAM}'>New quiz every week</div>
    </div>"""
    return _doc(body, TEAL_BRT)


# --- weekly series -----------------------------------------------------------------

def series_cover(series: str, episode: int, title: str, sub: str, image: str | None = None,
                 counter: str | None = None) -> str:
    pic = (f"<div style='flex:1;min-height:0;margin-top:44px;border-radius:40px;overflow:hidden;background:#e9eef0'>"
           f"<img src='{R._img_data_uri(image)}' style='width:100%;height:100%;object-fit:cover'></div>"
           if image else "<div style='flex:1'></div>")
    body = f"""
    {_mark(CREAM, counter)}
    <div class='serif' style='position:absolute;right:70px;top:150px;font-size:220px;line-height:1;color:transparent;
         -webkit-text-stroke:3px {TEAL_BRT};opacity:0.55'>{episode:02d}</div>
    <div style='position:absolute;left:84px;right:84px;top:180px;bottom:92px;display:flex;flex-direction:column'>
      <div style='display:flex;align-items:center;gap:22px'>
        <div class='pill' style='background:{CORAL};color:{CREAM}'>{_e(series)}</div>
        <div style='font-size:26px;font-weight:700;letter-spacing:0.1em;color:{TEAL_BRT}'>EPISODE {episode:02d}</div>
      </div>
      <div class='serif' style='font-size:92px;line-height:1.0;color:{CREAM};margin-top:40px;max-width:760px'>{_e(title)}</div>
      {pic}
      <div style='display:flex;justify-content:space-between;align-items:center;margin-top:40px'>
        <div style='font-size:32px;line-height:1.35;color:#b8cfd1;max-width:640px;font-weight:600'>{_e(sub)}</div>
        <div style='font-size:30px;font-weight:700;color:{TEAL_BRT}'>Swipe &rarr;</div>
      </div>
    </div>"""
    return _doc(body, INK)


def series_step(n: int, total: int, instruction: str, detail: str, counter: str | None = None) -> str:
    dots = "".join(f"<i style='display:block;width:{46 if i == n else 18}px;height:18px;border-radius:9px;"
                   f"background:{CORAL if i == n else 'rgba(13,26,27,0.15)'}'></i>" for i in range(1, total + 1))
    body = f"""
    {_mark(TEAL, counter)}
    <div style='position:absolute;left:84px;top:220px;display:flex;gap:10px;align-items:center'>{dots}</div>
    <div class='serif' style='position:absolute;left:66px;top:300px;font-size:420px;line-height:1;color:{TEAL}'>{n}</div>
    <div style='position:absolute;left:84px;right:84px;top:780px'>
      <div class='serif' style='font-size:80px;line-height:1.04;color:{INK}'>{_e(instruction)}</div>
      <div style='font-size:34px;line-height:1.5;color:{SOFT};margin-top:30px;max-width:880px'>{_e(detail)}</div>
    </div>"""
    return _doc(body, CREAM)
