"""
OralCheck Instagram Carousel — 6 slides, 1080x1350 (4:5 portrait)
Topic: HPV is now the #1 cause of oral cancer
Style: dark, bold typographic — proper textbbox measurement, visual fill elements
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H     = 1080, 1350
PAD      = 76
BG       = (13, 26, 27)
TEAL     = (13, 115, 119)
BRIGHT   = (20, 168, 174)
CORAL    = (232, 99, 74)
TEXT     = (232, 228, 222)
MUTED    = (90, 116, 118)
SUBTLE   = (22, 50, 52)
DIMMED   = (35, 62, 64)
DARK2    = (10, 20, 21)

FONT_DIR = "/Users/ianharris/Desktop/oralcheck/oralcheck-agent/fonts/"
OUT_DIR  = "/Users/ianharris/Desktop/oralcheck_carousel"
os.makedirs(OUT_DIR, exist_ok=True)

def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

S = "DMSerifDisplay-Regular.ttf"
N = "SourceSans3-Regular.ttf"

def text_h(draw, text, f, spacing=0):
    bb = draw.textbbox((0, 0), text, font=f, spacing=spacing)
    return bb[3] - bb[1]

def put(draw, x, y, text, f, color, spacing=0, max_w=None):
    """Draw text, wrapping if max_w set, return bottom y."""
    if max_w:
        words = text.split()
        lines, cur = [], []
        for w in words:
            test = " ".join(cur + [w])
            if draw.textlength(test, font=f) > max_w and cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))
        text = "\n".join(lines)
    draw.text((x, y), text, font=f, fill=color, spacing=spacing)
    bb = draw.textbbox((x, y), text, font=f, spacing=spacing)
    return bb[3]

def pill(draw, x, y, text, f, bg=SUBTLE, fg=MUTED):
    bb = draw.textbbox((0, 0), text, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    px, py = 18, 9
    draw.rounded_rectangle([(x, y), (x+tw+2*px, y+th+2*py)], radius=100, fill=bg)
    draw.text((x+px, y+py), text, font=f, fill=fg)
    return y + th + 2*py + 16

def brand_footer(draw):
    f = F(N, 26)
    draw.rectangle([(PAD, H-82), (PAD+44, H-78)], fill=BRIGHT)
    draw.text((PAD, H-66), "oralcheck.org", font=f, fill=BRIGHT)

def ring_motif(draw, cx, cy, alpha=255):
    """OralCheck logo ring motif as decorative art."""
    col = lambda r, g, b: (r, g, b)
    for r, w in [(260, 30), (108, 18)]:
        draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=SUBTLE, width=w)
    dot = 26
    ax = int(cx + 192 * math.cos(math.radians(-48)))
    ay = int(cy + 192 * math.sin(math.radians(-48)))
    draw.ellipse([(ax-dot, ay-dot), (ax+dot, ay+dot)], fill=CORAL)

def corner_deco(draw):
    ring_motif(draw, W + 40, -40)


# ─── SLIDE 1: Hook ──────────────────────────────────────────────────────────
def slide_1():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    corner_deco(draw)
    brand_footer(draw)

    f_tag = F(N, 22)
    y = pill(draw, PAD, 66, "ORAL HEALTH  ·  2025", f_tag)
    y += 28

    f_head = F(S, 100)
    f_sub  = F(N, 34)

    y = put(draw, PAD, y, "HPV is now", f_head, TEXT)
    y += 10
    y = put(draw, PAD, y, "the #1 cause", f_head, CORAL)
    y += 10
    y = put(draw, PAD, y, "of oral cancer.", f_head, TEXT)
    y += 44

    sub = "And most people under 50 have no idea they're at risk."
    y = put(draw, PAD, y, sub, f_sub, MUTED, spacing=10, max_w=W-PAD*2)
    y += 60

    # Visual fill: large centered ring constellation
    cx, cy = W // 2, y + 240
    ring_motif(draw, cx, cy)
    # Second smaller offset ring
    for r, w in [(130, 18), (54, 12)]:
        draw.ellipse([(cx+260-r, cy+100-r), (cx+260+r, cy+100+r)], outline=DIMMED, width=w)
    dot2 = 14
    draw.ellipse([(cx+330-dot2, cy+38-dot2), (cx+330+dot2, cy+38+dot2)], fill=TEAL)

    return img


# ─── SLIDE 2: The Scale ──────────────────────────────────────────────────────
def slide_2():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    corner_deco(draw)
    brand_footer(draw)

    f_tag  = F(N, 22)
    f_num  = F(S, 156)
    f_lbl  = F(N, 30)
    f_note = F(N, 21)

    y = pill(draw, PAD, 66, "THE NUMBERS", f_tag)
    y += 40

    # Big teal block behind 60,000
    block_h = 200
    draw.rectangle([(0, y-16), (W, y+block_h)], fill=DIMMED)
    y = put(draw, PAD, y, "60,000", F(S, 156), BRIGHT)
    y += 16
    y = put(draw, PAD, y, "new oral cancer cases in the US this year", f_lbl, MUTED,
            spacing=8, max_w=W-PAD*2)
    y += 50

    draw.rectangle([(PAD, y), (W-PAD, y+2)], fill=SUBTLE)
    y += 40

    # Big coral block behind 12,770
    draw.rectangle([(0, y-16), (W, y+block_h)], fill=(30, 18, 16))
    y = put(draw, PAD, y, "12,770", F(S, 156), CORAL)
    y += 16
    y = put(draw, PAD, y, "deaths — more than cervical cancer.", f_lbl, MUTED)
    y += 44

    draw.rectangle([(PAD, y), (PAD+36, y+3)], fill=SUBTLE)
    y += 16
    put(draw, PAD, y, "National Cancer Institute  ·  2025", f_note, DIMMED)

    return img


# ─── SLIDE 3: Survival Gap ───────────────────────────────────────────────────
def slide_3():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    brand_footer(draw)

    MID = H // 2

    # Top half — teal-dark block
    draw.rectangle([(0, 0), (W, MID)], fill=(10, 30, 32))
    # Bottom half — coral-dark block
    draw.rectangle([(0, MID), (W, H)], fill=(28, 14, 12))

    # Divider line
    draw.rectangle([(0, MID-1), (W, MID+1)], fill=(40, 20, 18))

    f_tag   = F(N, 22)
    f_label = F(S, 42)
    f_pct   = F(S, 200)
    f_word  = F(S, 52)
    f_sub   = F(N, 30)

    # Top: "Found early: / 87% / survive."
    pill(draw, PAD, 60, "THE CATCH", f_tag, (20, 55, 58), MUTED)

    y = 140
    y = put(draw, PAD, y, "Found early:", f_label, MUTED)
    y += 4
    y = put(draw, PAD, y, "87%", f_pct, BRIGHT)
    put(draw, PAD, y, "survive.", f_word, TEXT)

    # Bottom: "Found late: / 38% / survive."
    y = MID + 36
    y = put(draw, PAD, y, "Found late:", f_label, (130, 80, 70))
    y += 4
    y = put(draw, PAD, y, "38%", f_pct, CORAL)
    y = put(draw, PAD, y, "survive.", f_word, TEXT)
    y += 28

    put(draw, PAD, y, "Same cancer. Two very different outcomes.", f_sub, (60, 38, 34))

    return img


# ─── SLIDE 4: Why It's Missed ────────────────────────────────────────────────
def slide_4():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    corner_deco(draw)
    brand_footer(draw)

    f_tag  = F(N, 22)
    f_big  = F(S, 108)
    f_sub  = F(N, 33)
    f_note = F(N, 26)

    y = pill(draw, PAD, 66, "WHY IT'S MISSED", f_tag)
    y += 36

    y = put(draw, PAD, y, "It rarely", f_big, TEXT)
    y += 8
    y = put(draw, PAD, y, "hurts.", f_big, CORAL)
    y += 52

    sub = ("Early-stage oral cancer usually has no pain. "
           "By the time something feels wrong, it's often Stage III or IV.")
    y = put(draw, PAD, y, sub, f_sub, MUTED, spacing=12, max_w=W-PAD*2)
    y += 60

    # Large centered ring as visual anchor
    cx = W // 2
    cy = y + 250
    # Outer glow rings fading out
    for r, w, col in [
        (290, 2, DIMMED), (280, 2, DIMMED), (260, 28, SUBTLE),
        (110, 2, DIMMED), (100, 16, SUBTLE),
    ]:
        draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=col, width=w)

    # Coral dot at logo position
    dot = 28
    ax = int(cx + 195 * math.cos(math.radians(-46)))
    ay = int(cy + 195 * math.sin(math.radians(-46)))
    draw.ellipse([(ax-dot, ay-dot), (ax+dot, ay+dot)], fill=CORAL)

    # Inner question mark or X? — subtle "?" to represent the unknown
    f_q = F(S, 110)
    bb = draw.textbbox((0,0), "?", font=f_q)
    qw = bb[2]-bb[0]
    draw.text((cx - qw//2, cy - (bb[3]-bb[1])//2 - 10), "?",
              font=f_q, fill=SUBTLE)

    return img


# ─── SLIDE 5: The Solution ───────────────────────────────────────────────────
def slide_5():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    corner_deco(draw)
    brand_footer(draw)

    f_tag  = F(N, 22)
    f_huge = F(S, 200)
    f_word = F(S, 58)
    f_list = F(N, 32)

    y = pill(draw, PAD, 66, "WHAT YOU CAN DO", f_tag)
    y += 36

    bb2 = draw.textbbox((PAD, y), "2", font=f_huge)
    put(draw, PAD, y, "2", f_huge, BRIGHT)
    put(draw, bb2[2]+16, bb2[3]-70, "minutes.", f_word, TEXT)
    y = bb2[3] + 28

    draw.rectangle([(PAD, y), (PAD+52, y+3)], fill=BRIGHT)
    y += 28

    items = [
        "10 questions about your habits and risk factors.",
        "No account needed.",
        "Nothing stored.",
        "Just your result — instantly.",
    ]
    for i, item in enumerate(items):
        draw.ellipse([(PAD, y+12), (PAD+11, y+23)], fill=BRIGHT if i == 0 else SUBTLE)
        y = put(draw, PAD+22, y, item, f_list,
                TEXT if i == 0 else MUTED, max_w=W-PAD*2-22)
        y += 20

    y += 30
    # Ring motif fills lower portion
    ring_motif(draw, W // 2, y + 250)

    return img


# ─── SLIDE 6: CTA ───────────────────────────────────────────────────────────
def slide_6():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Large ring centered at 60% down — sits behind the text block
    ring_motif(draw, W//2, int(H*0.62))
    # Ghost outer ring
    for r, w in [(420, 2), (415, 1)]:
        draw.ellipse([(W//2-r, int(H*0.62)-r), (W//2+r, int(H*0.62)+r)],
                     outline=(16, 36, 38), width=w)

    f_big = F(S, 132)
    f_md  = F(S, 96)
    f_sub = F(N, 34)
    f_url = F(N, 48)

    # Vertically center text block in full canvas
    total = 132*3 + 96 + 36 + 52 + 60 + 54   # rough estimate
    y_start = (H - total) // 2 - 40

    y = max(y_start, 140)
    y = put(draw, PAD, y, "Free.", f_big, TEXT)
    y += 14
    y = put(draw, PAD, y, "Private.", f_big, BRIGHT)
    y += 14
    y = put(draw, PAD, y, "2 minutes.", f_md, TEXT)
    y += 52

    draw.rectangle([(PAD, y), (W-PAD, y+2)], fill=SUBTLE)
    y += 40

    y = put(draw, PAD, y, "Take the free oral cancer risk screener.", f_sub, MUTED)
    y += 60

    draw.rectangle([(PAD, y+6), (PAD+5, y+60)], fill=CORAL)
    put(draw, PAD+20, y+10, "oralcheck.org", f_url, BRIGHT)

    # Small brand footer
    f_footer = F(N, 24)
    draw.rectangle([(PAD, H-82), (PAD+44, H-78)], fill=BRIGHT)
    draw.text((PAD, H-66), "oralcheck.org", font=f_footer, fill=SUBTLE)

    return img


slides = [
    ("01_hook",     slide_1()),
    ("02_numbers",  slide_2()),
    ("03_survival", slide_3()),
    ("04_silent",   slide_4()),
    ("05_solution", slide_5()),
    ("06_cta",      slide_6()),
]

for name, img in slides:
    path = os.path.join(OUT_DIR, f"{name}.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"Saved: {path}")

print(f"\nAll {len(slides)} slides → {OUT_DIR}/")
