import os
"""Generate docs/poster/poster.html for OralCheck.

All weights below are copied from src/lib/questions.ts and src/lib/riskEngine.ts;
all epidemiology figures from src/lib/seerStats.ts. The figures are computed
from these tables so a number cannot appear in a figure that is not in a source.
"""
import math
import segno

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "poster.html")

TEAL = "#0d7377"
TEAL_DARK = "#095458"
TEAL_SOFT = "#e0f0f0"
CORAL = "#e8634a"
CORAL_DARK = "#c84d35"
WARM = "#faf9f6"
WARM_DIM = "#f0eee8"
INK = "#2d2d2d"
INK_SOFT = "#5f5f5f"
GREY = "#9a968e"
TIER = {
    "low": ("#7ba882", "#3d7346"),
    "moderate": ("#d4a03c", "#8a5f12"),
    "elevated": ("#e0874a", "#a8541c"),
    "high": ("#e8634a", "#b5432d"),
}

# ---- source data -----------------------------------------------------------
# seerStats.ts
SEER = dict(cases="60,480", deaths="13,150",
            surv=dict(localized=88.7, regional=69.7, distant=36.0),
            share=dict(localized=26, regional=55, distant=12, unknown=6),
            inc_m=17.5, inc_f=6.6, median_age=65)

K = 4.47

def formula(or_):
    return round(math.log(or_) * K)

# ---- QR --------------------------------------------------------------------

def qr_svg(url, px):
    q = segno.make(url, error="m")
    m = list(q.matrix)
    n = len(m)
    border = 2
    size = n + 2 * border
    d = []
    for y, row in enumerate(m):
        for x, v in enumerate(row):
            if v:
                d.append(f"M{x+border} {y+border}h1v1h-1z")
    return (f'<svg class="qr" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{px}" height="{px}" shape-rendering="crispEdges" role="img" '
            f'aria-label="QR code linking to {url}">'
            f'<rect width="{size}" height="{size}" fill="#ffffff"/>'
            f'<path fill="{INK}" d="{"".join(d)}"/></svg>')

# ---- Figure 1: survival by SEER summary stage --------------------------------

def fig_survival():
    W, H = 1060, 560
    s = []
    s.append(f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
             'aria-label="Five-year relative survival by SEER summary stage and share of cases diagnosed at each stage">')
    rows = [("Localized", "localized", TEAL), ("Regional", "regional", "#5c9ea0"), ("Distant", "distant", CORAL)]
    x0, bw = 250, 600
    s.append(f'<text x="0" y="40" font-size="34" font-weight="700" fill="{INK}">Five-year relative survival</text>')
    for i, (lab, key, col) in enumerate(rows):
        y = 80 + i * 92
        v = SEER["surv"][key]
        s.append(f'<text x="0" y="{y+50}" font-size="36" fill="{INK}">{lab}</text>')
        s.append(f'<rect x="{x0}" y="{y+8}" width="{bw}" height="60" fill="{WARM_DIM}"/>')
        s.append(f'<rect x="{x0}" y="{y+8}" width="{bw*v/100:.1f}" height="60" fill="{col}"/>')
        s.append(f'<text x="{x0+bw+18}" y="{y+52}" font-size="40" font-weight="700" fill="{INK}">{v:.1f}%</text>')
    # stage share stacked bar
    y = 380
    s.append(f'<text x="0" y="{y}" font-size="34" font-weight="700" fill="{INK}">Share of cases by stage at diagnosis</text>')
    order = [("localized", TEAL, "Localized"), ("regional", "#5c9ea0", "Regional"),
             ("distant", CORAL, "Distant"), ("unknown", "#c9c5bc", "")]
    total_w = W - 10
    tot = sum(SEER["share"].values())
    x = 0
    for key, col, lab in order:
        w = total_w * SEER["share"][key] / tot
        s.append(f'<rect x="{x:.1f}" y="{y+22}" width="{w-4:.1f}" height="74" fill="{col}"/>')
        txt = f'{SEER["share"][key]}%'
        tcol = "#ffffff" if key != "unknown" else INK
        s.append(f'<text x="{x+w/2-2:.1f}" y="{y+72}" font-size="36" font-weight="700" fill="{tcol}" text-anchor="middle">{txt}</text>')
        if lab:
            s.append(f'<text x="{x+w/2-2:.1f}" y="{y+140}" font-size="30" fill="{INK_SOFT}" text-anchor="middle">{lab}</text>')
        else:
            s.append(f'<text x="{x+w/2-2:.1f}" y="{y+140}" font-size="30" fill="{INK_SOFT}" text-anchor="middle">Unk.</text>')
        x += w
    s.append('</svg>')
    return "".join(s)

# ---- Figure 1b: stage share bar ---------------------------------------------

def fig_share():
    W, H = 1000, 150
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Share of cases by SEER summary stage at diagnosis">']
    order = [("localized", TEAL, "Localized"), ("regional", "#5c9ea0", "Regional"),
             ("distant", CORAL, "Distant"), ("unknown", "#c9c5bc", "")]
    tot = sum(SEER["share"].values())
    x = 0
    for key, col, lab in order:
        w = W * SEER["share"][key] / tot
        s.append(f'<rect x="{x:.1f}" y="0" width="{w-4:.1f}" height="84" fill="{col}"/>')
        tcol = "#ffffff" if key != "unknown" else INK
        s.append(f'<text x="{x+w/2-2:.1f}" y="56" font-size="38" font-weight="700" fill="{tcol}" text-anchor="middle">{SEER["share"][key]}%</text>')
        s.append(f'<text x="{x+w/2-2:.1f}" y="130" font-size="34" fill="{INK_SOFT}" text-anchor="middle">{lab or "Unk."}</text>')
        x += w
    s.append('</svg>')
    return "".join(s)

# ---- Figure 2: pipeline ------------------------------------------------------

def fig_pipeline():
    W, H = 1060, 520
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Scoring pipeline from twelve answers to a recommendation">']
    s.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>')

    def box(x, y, w, h, lines, fill=WARM_DIM, stroke=TEAL, tcol=INK, bold=False, size=38):
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="4"/>')
        n = len(lines)
        for i, ln in enumerate(lines):
            ty = y + h / 2 + (i - (n - 1) / 2) * (size * 1.18) + size * 0.35
            s.append(f'<text x="{x+w/2}" y="{ty:.1f}" font-size="{size}" font-weight="{"700" if bold else "400"}" fill="{tcol}" text-anchor="middle">{ln}</text>')

    def arrow(x1, y1, x2, y2):
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="4" marker-end="url(#ah)"/>')

    # row 1
    box(0, 0, 270, 170, ["12", "answers"], bold=True)
    arrow(272, 85, 318, 85)
    box(322, 0, 290, 170, ["Sum the", "weights"])
    arrow(614, 85, 660, 85)
    box(664, 0, 396, 170, ["+3 if tobacco", "and alcohol are", "both current"], fill="#fdf0ec", stroke=CORAL, size=36)
    s.append(f'<path d="M862 172 V 214 H 135 V 262" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#ah)"/>')
    # row 2
    box(0, 266, 270, 170, ["Score", "0 to 61"], fill=TEAL, stroke=TEAL, tcol="#ffffff", bold=True)
    arrow(272, 351, 318, 351)
    cx, cy, dw, dh = 470, 351, 300, 250
    s.append(f'<path d="M{cx} {cy-dh/2} L{cx+dw/2} {cy} L{cx} {cy+dh/2} L{cx-dw/2} {cy} Z" fill="#ffffff" stroke="{CORAL}" stroke-width="4"/>')
    for i, ln in enumerate(["Current", "symptom?"]):
        s.append(f'<text x="{cx}" y="{cy-8+i*44}" font-size="36" fill="{INK}" text-anchor="middle">{ln}</text>')
    s.append(f'<path d="M{cx+dw/2} {cy} H 650 V 311 H 676" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#ah)"/>')
    s.append(f'<path d="M650 {cy} V 448 H 676" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#ah)"/>')
    box(680, 250, 380, 122, ["Yes or unsure:", "See a dentist soon"], fill=TIER["high"][1], stroke=TIER["high"][1], tcol="#ffffff", bold=True, size=35)
    box(680, 398, 380, 100, ["No: tier by score"], size=36)
    s.append('</svg>')
    return "".join(s)

# ---- Figure 3: derivation ----------------------------------------------------
# (OR used by the formula, assigned weight, label); ranges use their midpoint
# except tobacco daily, which is the anchor at the top of its range.
POINTS = [
    (1.2, 1, "alcohol rarely"), (1.2, 1, "HPV unknown"), (1.2, 1, "immune unsure"),
    (1.3, 1, "family distant"), (1.3, 1, "diet weekly"),
    (1.5, 2, "age 35-54"), (1.5, 2, "tobacco former"), (1.5, 2, "HPV not vaccinated"),
    (2.0, 3, "alcohol weekly"), (2.0, 3, "family"), (2.0, 3, "diet low"), (2.0, 3, "male"),
    (2.15, 3, "interaction"),
    (2.5, 4, "age 55-64"), (2.5, 4, "betel past"),
    (3.0, 5, "tobacco occasional"), (3.0, 5, "alcohol daily"), (3.0, 5, "immune yes"),
    (4.0, 6, "age 65+"),
    (6.0, 8, "tobacco daily"),
]
DEPART = [  # (OR used, formula, assigned, label)
    (8.5, None, 9, "Betel, current"),
    (4.0, None, 5, "HPV history"),
    (2.5, None, 2, "Sun, daily"),
    (1.5, None, 1, "Sun, regular"),
]

def fig_derivation():
    for o, w, lab in POINTS:
        assert formula(o) == w, (o, w, lab)
    W, H = 1060, 1150
    L, R, T, B = 110, 30, 20, 120
    pw, ph = W - L - R, H - T - B
    xmax, ymax = math.log(10), 10.6

    def X(o):
        return L + pw * math.log(o) / xmax

    def Y(w):
        return T + ph * (1 - w / ymax)

    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Assigned weight against odds ratio on a log scale, with the formula line">']
    # grid + axes
    for w in range(0, 11, 2):
        s.append(f'<line x1="{L}" y1="{Y(w):.1f}" x2="{W-R}" y2="{Y(w):.1f}" stroke="#e4e1da" stroke-width="2"/>')
        s.append(f'<text x="{L-18}" y="{Y(w)+12:.1f}" font-size="32" fill="{INK_SOFT}" text-anchor="end">{w}</text>')
    for o in [1, 1.5, 2, 3, 4, 6, 10]:
        s.append(f'<line x1="{X(o):.1f}" y1="{T+ph}" x2="{X(o):.1f}" y2="{T+ph+12}" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<text x="{X(o):.1f}" y="{T+ph+52}" font-size="32" fill="{INK_SOFT}" text-anchor="middle">{o:g}</text>')
    s.append(f'<line x1="{L}" y1="{T+ph}" x2="{W-R}" y2="{T+ph}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+ph}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<text x="{L+pw/2}" y="{H-14}" font-size="34" fill="{INK}" text-anchor="middle">Odds ratio (log scale)</text>')
    s.append(f'<text transform="translate(36 {T+ph/2}) rotate(-90)" font-size="34" fill="{INK}" text-anchor="middle">Points</text>')
    # formula line
    s.append(f'<line x1="{X(1):.1f}" y1="{Y(0):.1f}" x2="{X(10):.1f}" y2="{Y(K*math.log(10)):.1f}" '
             f'stroke="{TEAL}" stroke-width="4" stroke-dasharray="14 10"/>')
    s.append(f'<text x="{X(1.32):.1f}" y="{Y(6.2):.1f}" font-size="34" font-weight="700" fill="{TEAL_DARK}">4.47 × ln(OR)</text>')
    # on-formula points, grouped
    groups = {}
    for o, w, lab in POINTS:
        groups.setdefault((o, w), []).append(lab)
    for (o, w), labs in groups.items():
        r = 15 + 3 * (len(labs) - 1)
        s.append(f'<circle cx="{X(o):.1f}" cy="{Y(w):.1f}" r="{r}" fill="{TEAL}" stroke="#ffffff" stroke-width="3"/>')
        if len(labs) > 1:
            if o == 1.3:
                s.append(f'<text x="{X(o):.1f}" y="{Y(w)-r-10:.1f}" font-size="30" fill="{TEAL_DARK}" text-anchor="middle" font-weight="700">×{len(labs)}</text>')
            else:
                s.append(f'<text x="{X(o)-r-6:.1f}" y="{Y(w)-r+4:.1f}" font-size="30" fill="{TEAL_DARK}" text-anchor="end" font-weight="700">×{len(labs)}</text>')
    # anchor label
    s.append(f'<text x="{X(6.0)-28:.1f}" y="{Y(8)+12:.1f}" font-size="32" font-weight="700" fill="{TEAL_DARK}" text-anchor="end">Anchor: daily tobacco, 8</text>')
    # departures
    for o, _, a, lab in DEPART:
        f = formula(o)
        s.append(f'<circle cx="{X(o):.1f}" cy="{Y(f):.1f}" r="15" fill="#ffffff" stroke="{CORAL}" stroke-width="4"/>')
        s.append(f'<line x1="{X(o):.1f}" y1="{Y(f)+17:.1f}" x2="{X(o):.1f}" y2="{Y(a)-19:.1f}" stroke="{CORAL}" stroke-width="4"/>')
        s.append(f'<rect x="{X(o)-15:.1f}" y="{Y(a)-15:.1f}" width="30" height="30" fill="{CORAL}" transform="rotate(45 {X(o):.1f} {Y(a):.1f})"/>')
        s.append(f'<text x="{X(o)+26:.1f}" y="{Y(a)+11:.1f}" font-size="32" font-weight="700" fill="{CORAL_DARK}">{lab}: {a} (formula {f})</text>'
                 if o < 6 else
                 f'<text x="{X(o)-28:.1f}" y="{Y(f)+11:.1f}" font-size="32" font-weight="700" fill="{CORAL_DARK}" text-anchor="end">{lab}: {a} (formula {f})</text>')
    s.append('</svg>')
    return "".join(s)

# ---- Figure 4: tier scale ----------------------------------------------------

def fig_tiers():
    W, H = 1000, 330
    L, R = 4, 6
    split = 30            # linear 0..30, then an axis break to 61
    brk = 60
    lin_w = W - L - R - brk

    def X(v):
        return L + lin_w * v / (split + 1)

    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Score scale from 0 to 61 with four tiers and four reference profiles">']
    y0, bh = 96, 130
    bands = [("low", 0, 4, "Low", "0–4"), ("moderate", 5, 13, "Moderate", "5–13"),
             ("elevated", 14, 22, "Elevated", "14–22"), ("high", 23, 61, "High", "23+")]
    for key, a, b, name, rng in bands:
        x1 = X(a)
        x2 = X(b + 1) if b < 61 else W - R
        col, strong = TIER[key]
        s.append(f'<rect x="{x1:.1f}" y="{y0}" width="{x2-x1-3:.1f}" height="{bh}" fill="{col}"/>')
        s.append(f'<text x="{(x1+x2)/2:.1f}" y="{y0+56}" font-size="36" font-weight="700" fill="#ffffff" text-anchor="middle">{name}</text>')
        s.append(f'<text x="{(x1+x2)/2:.1f}" y="{y0+104}" font-size="36" fill="#ffffff" text-anchor="middle">{rng}</text>')
    bx = X(split + 1) + brk / 2 - 6
    s.append(f'<rect x="{bx-16}" y="{y0-6}" width="32" height="{bh+12}" fill="#ffffff"/>')
    for dx in (-10, 10):
        s.append(f'<line x1="{bx+dx-10}" y1="{y0+bh+10}" x2="{bx+dx+10}" y2="{y0-10}" stroke="{INK}" stroke-width="4"/>')
    for v in [0, 5, 14, 23]:
        s.append(f'<line x1="{X(v):.1f}" y1="{y0+bh}" x2="{X(v):.1f}" y2="{y0+bh+16}" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<text x="{X(v)+(14 if v==0 else 0):.1f}" y="{y0+bh+56}" font-size="34" fill="{INK_SOFT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{W-R}" y="{y0+bh+56}" font-size="34" fill="{INK_SOFT}" text-anchor="end">61</text>')
    for v in [3, 8, 16, 25]:
        x = X(v + 0.5)
        s.append(f'<path d="M{x-16:.1f} {y0-26} L{x+16:.1f} {y0-26} L{x:.1f} {y0-2} Z" fill="{INK}"/>')
        s.append(f'<text x="{x:.1f}" y="{y0-38}" font-size="40" font-weight="700" fill="{INK}" text-anchor="middle">{v}</text>')
    s.append('</svg>')
    return "".join(s)

# ---- Table 1 -----------------------------------------------------------------
# (question, [(answer, points)], OR basis, refs)
TABLE = [
    ("Age", [("&lt;35", 0), ("35–54", 2), ("55–64", 4), ("65+", 6)], "1.5 / 2.5 / 4.0, adjusted", "7"),
    ("Sex at birth", [("Male", 3), ("Female", 0), ("Not stated", 2)], "2.0 (SEER ratio 2.6)*", "7"),
    ("Tobacco", [("Daily", 8), ("Occasional", 5), ("Former", 2), ("Never", 0)], "6.0 / 3.0 / 1.5", "1"),
    ("Alcohol", [("Daily", 5), ("Weekly", 3), ("Rarely", 1), ("Never", 0)], "3.0 / 2.0 / 1.2", "2"),
    ("HPV", [("History", 5), ("Unvaccinated", 2), ("Unsure", 1), ("Vaccinated", 0)], "3–5 / 1.5 / 1.2, proxies", "3, 10"),
    ("Lip sun exposure", [("Daily", 2), ("Regular", 1), ("Minimal", 0)], "2–3 / 1.5, lip only", "11"),
    ("Current symptom, 2+ wk", [("Yes", 6), ("Unsure", 3), ("No", 0)], "Override, not an OR", "5"),
    ("Family history", [("Close", 3), ("Distant", 1), ("No / unsure", 0)], "2.0 / 1.3", "9"),
    ("Immune or radiation", [("Yes", 5), ("Unsure", 1), ("No", 0)], "2–4 blended / 1.2", "12, 13"),
    ("Fruit and vegetables", [("Daily", 0), ("Weekly", 1), ("Rarely", 3)], "1.3 / 2.0 (low intake)", "6"),
    ("Last dental visit", [("&lt;1 yr", 0), ("1–3 yr", 1), ("3+ yr", 2), ("Never", 3)], "Detection proxy, not an OR", "14"),
    ("Betel quid / paan", [("Current", 9), ("Past", 4), ("Never", 0)], "7–10 / 2.5", "4"),
]

def table_html():
    # departures and non-OR answers are flagged
    depart = {("HPV", "History"), ("Lip sun exposure", "Daily"), ("Lip sun exposure", "Regular"), ("Betel quid / paan", "Current")}
    nonor = {("Sex at birth", "Not stated"), ("Current symptom, 2+ wk", "Yes"), ("Current symptom, 2+ wk", "Unsure"),
             ("Last dental visit", "1–3 yr"), ("Last dental visit", "3+ yr"), ("Last dental visit", "Never")}
    rows = []
    total = 0
    for q, opts, orb, ref in TABLE:
        total += max(p for _, p in opts)
        chips = []
        for a, p in opts:
            cls = "chip"
            if (q, a) in depart:
                cls += " dep"
            elif (q, a) in nonor:
                cls += " non"
            elif p == 0:
                cls += " zero"
            chips.append(f'<span class="{cls}">{a} <b>{p}</b></span>')
        rows.append(f'<tr><th scope="row">{q}</th><td>{"".join(chips)}<div class="orb">OR {orb} <span class="ref">[{ref}]</span></div></td></tr>'
                    if not orb.startswith(("Override", "Detection")) else
                    f'<tr><th scope="row">{q}</th><td>{"".join(chips)}<div class="orb">{orb} <span class="ref">[{ref}]</span></div></td></tr>')
    rows.append('<tr class="int"><th scope="row">Tobacco and alcohol</th><td><span class="chip">Both current <b>+3</b></span>'
                '<div class="orb">Interaction parameter 2.15 <span class="ref">[8]</span></div></td></tr>')
    assert total == 58 and total + 3 == 61
    return "".join(rows)

REFS = [
    "Gandini S, Botteri E, Iodice S, et al. Int J Cancer. 2008;122(1):155–164.",
    "Bagnardi V, Rota M, Botteri E, et al. Br J Cancer. 2015;112(3):580–593.",
    "Gillison ML, D’Souza G, Westra W, et al. J Natl Cancer Inst. 2008;100(6):407–420.",
    "International Agency for Research on Cancer. IARC Monograph 85: Betel-quid and areca-nut chewing. Lyon: IARC; 2004.",
    "Napier SS, Speight PM. J Oral Pathol Med. 2008;37(1):1–10.",
    "Pavia M, Pileggi C, Nobile CG, Angelillo IF. Am J Clin Nutr. 2006;83(5):1126–1134.",
    "National Cancer Institute. SEER Cancer Statistics Review 1975–2021.",
    "Hashibe M, Brennan P, Chuang SC, et al. Cancer Epidemiol Biomarkers Prev. 2009;18(2):541–550.",
    "Negri E, Boffetta P, Berthiller J, et al. Int J Cancer. 2009;124(2):394–401.",
    "D’Souza G, Kreimer AR, Viscidi R, et al. N Engl J Med. 2007;356(19):1944–1956.",
    "Perea-Milla López E, Minarro-Del Moral RM, Martinez-Garcia C, et al. Br J Cancer. 2003;88(11):1702–1707.",
    "Engels EA, Pfeiffer RM, Fraumeni JF Jr, et al. JAMA. 2011;306(17):1891–1901.",
    "Grulich AE, van Leeuwen MT, Falster MO, Vajdic CM. Lancet. 2007;370(9581):59–67.",
    "National Cancer Institute. SEER Cancer Stat Facts: Oral Cavity and Pharynx Cancer. Accessed 30 August 2026.",
]


LAYOUT = [
    ["background", "objective", "design", "pipeline"],
    ["formula", "deriv", "depart"],
    ["table", "tiers"],
    ["review", "limits", "next", "refs"],
]

def build():
    D = os.path.dirname(os.path.abspath(__file__)) + "/"
    head = open(D + "head.html").read()
    raw = open(D + "sections.html").read()
    secs = {}
    for chunk in raw.split("<!--@")[1:]:
        name, body = chunk.split("-->", 1)
        secs[name.strip()] = body
    used = [n for c in LAYOUT for n in c]
    assert sorted(used) == sorted(secs), (sorted(used), sorted(secs))
    cols = "".join('<div class="col">' + "".join(secs[n].replace("<section>", f'<section id="{n}">', 1) for n in c) + "</div>\n" for c in LAYOUT)
    html = head + "\n<main>\n" + cols + "</main>\n</div>\n</body>\n</html>\n"
    repl = {
        "{{QR}}": qr_svg("https://oralcheck.org", 560),
        "{{FIG_SHARE}}": fig_share(),
        "{{FIG_PIPE}}": fig_pipeline(),
        "{{FIG_DERIV}}": fig_derivation(),
        "{{FIG_TIERS}}": fig_tiers(),
        "{{TABLE}}": table_html(),
        "{{REFS}}": "".join(f"<li>{r}</li>" for r in REFS),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    assert "{{" not in html
    assert "—" not in html, "em dash found"
    assert "!" not in html.replace("<!doctype", "").replace("<!--", ""), "exclamation found"
    for bad in ("UW", "Wisconsin", "Madison", "Rawal", "Brant", "Marquette", "validated tool"):
        assert bad not in html, bad
    open(OUT, "w").write(html)
    print("wrote", OUT, len(html))


if __name__ == "__main__":
    build()
