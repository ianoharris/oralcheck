"""
Code-drawn illustrations and icons for posts and reels.

Everything here is hand-built SVG, so it costs nothing to render, scales to
any size, and can be animated deterministically in the reel engine (every
zone and icon is addressable by id). No stock art, no generated imagery.

The mouth map follows the site's own self-exam guide
(src/app/[locale]/learn/self-exam): lips, cheeks, gums, tongue, floor of mouth,
roof of mouth, throat. Face and neck is the eighth step and gets its own icon,
because a front view of an open mouth cannot show it.
"""
from __future__ import annotations

# Flat, slightly warm tissue tones. Chosen to read as a mouth at a glance
# without looking clinical or graphic.
TISSUE = {
    "lip": "#d9776a",
    "lip_shade": "#c4615a",
    "cavity": "#4a141b",
    "throat": "#26080c",
    "palate": "#b9545a",
    "palate_ridge": "#a8484f",
    "cheek": "#c45b63",
    "gum": "#e98f8c",
    "tooth": "#f7f0e3",
    "tooth_line": "#e2d6c2",
    "tongue": "#d6646b",
    "tongue_shade": "#c2535b",
    "uvula": "#cf6a6f",
}

HIGHLIGHT = "#f2c14e"   # amber: reads clearly against every tissue tone

# Zone order matches the site's self-exam steps (face and neck aside).
ZONES = ["lips", "cheeks", "gums", "tongue", "floor", "roof", "throat"]
ZONE_LABELS = {
    "lips": "Lips",
    "cheeks": "Cheeks",
    "gums": "Gums",
    "tongue": "Tongue, top and sides",
    "floor": "Floor of mouth",
    "roof": "Roof of mouth",
    "throat": "Throat",
}
# Where each numbered badge sits in the 600x500 mouth-map coordinate space.
ZONE_BADGES = {
    "lips": (300, 124),
    "cheeks": (124, 262),
    "gums": (414, 178),
    "tongue": (360, 304),
    "floor": (300, 368),
    "roof": (248, 222),
    "throat": (338, 244),
}


def _arc_y_top(x: float) -> float:
    return 140 + 0.00282 * (x - 300) ** 2


def _arc_y_bot(x: float) -> float:
    return 412 - 0.00347 * (x - 300) ** 2


def _teeth(upper: bool) -> str:
    """A row of teeth that follows the curve of the mouth opening."""
    out = []
    xs = [138, 170, 203, 236, 268, 300, 332, 364, 397, 430, 462]
    for x in xs:
        d = abs(x - 300)
        w = 30 - d * 0.03
        h = (44 if upper else 36) - d * 0.06
        if upper:
            y = _arc_y_top(x) + 10
        else:
            y = _arc_y_bot(x) - 10 - h
        out.append(
            f"<rect x='{x - w / 2:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' "
            f"rx='{w * 0.32:.1f}' fill='{TISSUE['tooth']}' stroke='{TISSUE['tooth_line']}' stroke-width='1.5'/>"
        )
    return "".join(out)


def _gum_band(upper: bool) -> str:
    pts_outer, pts_inner = [], []
    for i in range(0, 41):
        x = 118 + i * (364 / 40)
        if upper:
            y = _arc_y_top(x)
            pts_outer.append((x, y - 2))
            pts_inner.append((x, y + 16))
        else:
            y = _arc_y_bot(x)
            pts_outer.append((x, y + 2))
            pts_inner.append((x, y - 14))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_outer)
    path += " L " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in reversed(pts_inner)) + " Z"
    return path


OUTER_LIP = ("M 40,262 C 70,170 170,92 248,96 C 268,97 284,106 300,112 "
             "C 316,106 332,97 352,96 C 430,92 530,170 560,262 "
             "C 530,380 420,455 300,458 C 180,455 70,380 40,262 Z")
INNER_MOUTH = ("M 92,262 C 120,190 210,140 300,140 C 390,140 480,190 508,262 "
               "C 480,350 400,410 300,412 C 200,410 120,350 92,262 Z")
# Drawn a little higher than a resting tongue so a sliver of the floor of the
# mouth shows beneath it; otherwise that self-exam step has nothing to point at.
TONGUE = ("M 172,340 C 180,280 242,262 300,262 C 358,262 420,280 428,340 "
          "C 390,356 210,356 172,340 Z")
PALATE = "M 168,212 C 196,168 404,168 432,212 C 380,236 220,236 168,212 Z"
THROAT = "M 248,252 C 258,226 342,226 352,252 C 346,292 254,292 248,252 Z"
UVULA = "M 291,226 C 291,244 293,256 300,258 C 307,256 309,244 309,226 Z"
FLOOR = "M 186,344 C 236,362 364,362 414,344 L 414,392 C 364,384 236,384 186,392 Z"

# Tongue-raised pose, for the floor-of-mouth step: the tip lifted to the roof,
# so the underside, the frenulum and the floor beneath are all in view.
TONGUE_UP = "M 170,246 C 176,170 424,170 430,246 C 414,296 186,296 170,246 Z"
FLOOR_UP = "M 128,300 C 190,262 410,262 472,300 C 452,388 148,388 128,300 Z"


def _zone_shapes(pose: str = "open") -> dict[str, str]:
    """The highlight geometry for each zone, drawn over the base illustration."""
    up = pose == "tongue_up"
    return {
        "lips": f"<path d='{OUTER_LIP} {INNER_MOUTH}' fill-rule='evenodd'/>",
        "cheeks": ("<ellipse cx='128' cy='262' rx='30' ry='66'/>"
                   "<ellipse cx='472' cy='262' rx='30' ry='66'/>"),
        "gums": f"<path d='{_gum_band(True)}'/><path d='{_gum_band(False)}'/>",
        "tongue": f"<path d='{TONGUE_UP if up else TONGUE}'/>",
        "floor": f"<path d='{FLOOR_UP if up else FLOOR}'/>",
        "roof": f"<path d='{PALATE}'/>",
        "throat": f"<path d='{THROAT}'/>",
    }


def mouth_map(highlight: list[str] | None = None, badges: list[str] | None = None,
              animated: bool = False, uid: str = "m", pose: str = "open") -> str:
    """Front view of an open mouth, 600x500.

    highlight: zones drawn with the amber highlight (static posts).
    badges:    zones that get a numbered badge, numbered in the order given.
    animated:  every zone overlay and badge is emitted at opacity 0 with an id
               (`{uid}-z-{zone}`, `{uid}-b-{zone}`) so the reel runtime can
               bring them in on cue.
    pose:      "open" (resting tongue) or "tongue_up" (tip lifted to the roof,
               which is the only view that actually shows the floor of the mouth).
    """
    highlight = highlight or []
    badges = badges if badges is not None else []
    clip = f"{uid}-clip"
    zones = _zone_shapes(pose)

    def overlay(name: str) -> str:
        on = name in highlight and not animated
        return (
            f"<g id='{uid}-z-{name}' class='zone' fill='{HIGHLIGHT}' "
            f"fill-opacity='0.78' stroke='#fff6d8' stroke-width='3' "
            f"style='opacity:{1 if on else 0}'>{zones[name]}</g>"
        )

    badge_svg = []
    for i, name in enumerate(badges, 1):
        bx, by = ZONE_BADGES[name]
        on = not animated
        badge_svg.append(
            f"<g id='{uid}-b-{name}' class='badge' style='opacity:{1 if on else 0};"
            f"transform-box:view-box;transform-origin:{bx}px {by}px'>"
            f"<circle cx='{bx}' cy='{by}' r='22' fill='#e8634a' stroke='#fff8f0' stroke-width='4'/>"
            f"<text x='{bx}' y='{by + 8}' text-anchor='middle' font-family='Source Sans 3, sans-serif' "
            f"font-weight='900' font-size='24' fill='#fff8f0'>{i}</text></g>"
        )

    # Layering matters: each highlight sits directly above the tissue it marks
    # and below anything in front of that tissue, so a highlighted tongue does
    # not paint over the lower teeth.
    return (
        f"<svg viewBox='0 0 600 500' xmlns='http://www.w3.org/2000/svg' class='mouthmap'>"
        f"<defs><clipPath id='{clip}'><path d='{INNER_MOUTH}'/></clipPath></defs>"
        f"<path d='{OUTER_LIP}' fill='{TISSUE['lip']}'/>"
        f"<path d='M 70,262 C 120,330 200,372 300,374 C 400,372 480,330 530,262 "
        f"C 500,370 410,436 300,438 C 190,436 100,370 70,262 Z' fill='{TISSUE['lip_shade']}' opacity='0.55'/>"
        f"<g clip-path='url(#{clip})'>"
        f"<rect x='0' y='0' width='600' height='500' fill='{TISSUE['cavity']}'/>"
        f"<ellipse cx='128' cy='262' rx='30' ry='66' fill='{TISSUE['cheek']}'/>"
        f"{overlay('cheeks')}"
        f"<path d='{PALATE}' fill='{TISSUE['palate']}'/>"
        f"<path d='M 300,180 L 300,226 M 260,190 Q 280,200 300,198 Q 320,200 340,190' "
        f"stroke='{TISSUE['palate_ridge']}' stroke-width='4' fill='none' stroke-linecap='round'/>"
        f"{overlay('roof')}"
        f"{_inner(pose, overlay)}"
        f"<path d='{_gum_band(True)}' fill='{TISSUE['gum']}'/>"
        f"<path d='{_gum_band(False)}' fill='{TISSUE['gum']}'/>"
        f"{overlay('gums')}"
        f"{_teeth(True)}{_teeth(False)}"
        f"</g>"
        f"{overlay('lips')}"
        f"{''.join(badge_svg)}"
        f"</svg>"
    )


def _inner(pose: str, overlay) -> str:
    """Throat, tongue and floor, which are what change between poses."""
    if pose == "tongue_up":
        return (
            f"<path d='{FLOOR_UP}' fill='#cf6f78'/>"
            f"<path d='M 220,318 C 250,336 280,340 296,338 M 380,318 C 350,336 320,340 304,338' "
            f"stroke='#b85862' stroke-width='4' fill='none' stroke-linecap='round'/>"
            f"{overlay('floor')}"
            f"<path d='{TONGUE_UP}' fill='#dc7c87'/>"
            f"<path d='M 262,206 C 270,240 278,262 286,284 M 338,206 C 330,240 322,262 314,284' "
            f"stroke='#9b5a86' stroke-width='5' fill='none' stroke-linecap='round' opacity='0.8'/>"
            f"{overlay('tongue')}"
            f"<path d='M 300,286 C 298,304 298,322 300,340' stroke='#c25f69' stroke-width='9' "
            f"fill='none' stroke-linecap='round'/>"
        )
    return (
        f"<path d='{THROAT}' fill='{TISSUE['throat']}'/>"
        f"{overlay('throat')}"
        f"<path d='{UVULA}' fill='{TISSUE['uvula']}'/>"
        f"<path d='{FLOOR}' fill='{TISSUE['tongue_shade']}'/>"
        f"{overlay('floor')}"
        f"<path d='{TONGUE}' fill='{TISSUE['tongue']}'/>"
        f"<path d='M 300,274 C 302,298 300,322 300,346' stroke='{TISSUE['tongue_shade']}' "
        f"stroke-width='5' fill='none' stroke-linecap='round'/>"
        f"{overlay('tongue')}"
    )


# ---------------------------------------------------------------------------
# Icons. 48x48, stroke-based, one colour, so they sit on any background.
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "tobacco": ("<rect x='5' y='27' width='34' height='8' rx='2'/>"
                "<path d='M31 27v8'/><path d='M41 22c3-3-3-6 0-9s-3-6 0-9'/>"),
    "alcohol": ("<path d='M15 6h18c0 11-3.5 18-9 18s-9-7-9-18z'/>"
                "<path d='M24 24v14'/><path d='M16 42h16'/><path d='M16 13h16'/>"),
    "sun": ("<circle cx='24' cy='24' r='8'/>"
            "<path d='M24 4v6M24 38v6M4 24h6M38 24h6M9.9 9.9l4.2 4.2M33.9 33.9l4.2 4.2"
            "M9.9 38.1l4.2-4.2M33.9 14.1l4.2-4.2'/>"),
    "hpv": ("<circle cx='24' cy='24' r='10'/>"
            "<path d='M24 6v8M24 34v8M6 24h8M34 24h8M11.3 11.3l5.6 5.6M31.1 31.1l5.6 5.6"
            "M11.3 36.7l5.6-5.6M31.1 16.9l5.6-5.6'/>"
            "<circle cx='24' cy='5' r='2'/><circle cx='24' cy='43' r='2'/>"
            "<circle cx='5' cy='24' r='2'/><circle cx='43' cy='24' r='2'/>"),
    "betel": ("<path d='M9 39C9 19 24 8 40 8c0 17-12 31-31 31z'/><path d='M9 39L32 16'/>"
              "<path d='M18 30l-6-1M24 24l-6-1M24 24l1-6M18 30l1-6'/>"),
    "family": ("<circle cx='16' cy='14' r='5'/><circle cx='33' cy='17' r='4'/>"
               "<path d='M6 40c0-9 4.5-15 10-15s10 6 10 15'/>"
               "<path d='M26 40c0-7 3-12 7-12s8 5 8 12'/>"),
    "calendar": ("<rect x='6' y='9' width='36' height='33' rx='4'/><path d='M6 19h36M16 5v8M32 5v8'/>"
                 "<path d='M14 27h4M22 27h4M30 27h4M14 34h4M22 34h4'/>"),
    "mirror": ("<circle cx='22' cy='19' r='13'/><path d='M31 28l11 13'/>"
               "<path d='M16 14c2-3 5-4 8-4'/>"),
    "light": ("<rect x='4' y='19' width='16' height='10' rx='2'/><path d='M20 17l9-5v24l-9-5z'/>"
              "<path d='M34 15l7-4M35 24h8M34 33l7 4'/>"),
    "search": "<circle cx='20' cy='20' r='12'/><path d='M29 29l12 12'/>",
    "check": "<path d='M10 25l9 9 19-20'/>",
    "cross": "<path d='M13 13l22 22M35 13L13 35'/>",
    "alert": ("<path d='M24 6l20 35H4z'/><path d='M24 19v10'/>"
              "<circle cx='24' cy='35' r='1.5'/>"),
    "tooth": ("<path d='M14 7c-6 0-9 5-8 11 1 5 3 7 4 13 1 5 2 10 5 10s3-8 5-12c1-2 3-2 4 0 2 4 2 12 5 12"
              "s4-5 5-10c1-6 3-8 4-13 1-6-2-11-8-11-4 0-6 2-8 2s-4-2-8-2z'/>"),
    "clock": "<circle cx='24' cy='24' r='18'/><path d='M24 13v12l8 5'/>",
    "neck": ("<circle cx='24' cy='14' r='9'/><path d='M19 22v6M29 22v6'/>"
             "<path d='M8 44c0-9 7-15 16-15s16 6 16 15'/><path d='M15 27h4M29 27h4'/>"),
    "hand": ("<path d='M17 26V10a3 3 0 016 0v13M23 22V7a3 3 0 016 0v15M29 22V10a3 3 0 016 0v14"
             "M17 24v-5a3 3 0 00-6 0v9c0 9 6 15 13 15h2c7 0 11-6 11-13v-8a3 3 0 00-6 0'/>"),
    "chat": "<path d='M6 10h36v22H20l-9 8v-8H6z'/>",
    "clinic": ("<path d='M6 42V18l18-11 18 11v24z'/><path d='M24 20v12M18 26h12'/>"
               "<path d='M19 42v-6h10v6'/>"),
    "school": ("<path d='M4 18l20-10 20 10-20 10z'/><path d='M12 22v10c0 4 6 7 12 7s12-3 12-7V22'/>"
               "<path d='M44 18v12'/>"),
    "pin": "<path d='M24 44S9 29 9 19a15 15 0 0130 0c0 10-15 25-15 25z'/><circle cx='24' cy='19' r='5'/>",
    "vaccine": ("<path d='M30 6l12 12M36 12l-6 6M33 9L13 29l6 6 20-20'/><path d='M13 29l-7 7 6 6 7-7'/>"
                "<path d='M20 22l4 4M24 18l4 4'/>"),
    "microscope": ("<path d='M18 6l8 3-6 16-8-3z'/><path d='M16 25l-2 5'/><path d='M8 42h32'/>"
                   "<path d='M26 18a12 12 0 016 22'/><path d='M14 36h14'/>"),
    "ear": ("<path d='M14 20a11 11 0 0122 0c0 7-6 9-7 14s-3 9-8 9c-3 0-5-2-5-4'/>"
            "<path d='M20 21a5 5 0 0110 0c0 3-3 4-3 7'/>"),
    "dollar": ("<circle cx='24' cy='24' r='18'/><path d='M24 12v24'/>"
               "<path d='M30 18c-1-2-3-3-6-3-4 0-6 2-6 4.5s2 3.5 6 4.5 6 2 6 4.5-2 4.5-6 4.5c-3 0-5-1-6-3'/>"),
}


def icon(name: str, color: str = "currentColor", size: int = 48, stroke: float = 3.2,
         id_attr: str = "", extra_style: str = "") -> str:
    body = _ICON_PATHS[name]
    ida = f" id='{id_attr}'" if id_attr else ""
    return (
        f"<svg{ida} viewBox='0 0 48 48' width='{size}' height='{size}' fill='none' stroke='{color}' "
        f"stroke-width='{stroke}' stroke-linecap='round' stroke-linejoin='round' "
        f"style='{extra_style}' xmlns='http://www.w3.org/2000/svg'>{body}</svg>"
    )


ICONS = tuple(_ICON_PATHS)


def calendar_grid(days: int = 14, flag_day: int = 15, cols: int = 5, cell: int = 120,
                  gap: int = 16, fill: str = "#0d7377", flag: str = "#e8634a",
                  text: str = "#f4f1ea", empty: str = "rgba(255,255,255,0.12)",
                  animated: bool = False, uid: str = "cal") -> str:
    """A grid of day cells, days 1..`days` filled, `flag_day` flagged.

    With `animated`, every cell starts transparent and carries an id
    (`{uid}-d{n}`) for the reel runtime to fill in sequence.
    """
    total = flag_day
    rows = (total + cols - 1) // cols
    w = cols * cell + (cols - 1) * gap
    h = rows * cell + (rows - 1) * gap
    out = [f"<svg viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg' class='calgrid'>"]
    for n in range(1, total + 1):
        r, c = divmod(n - 1, cols)
        x, y = c * (cell + gap), r * (cell + gap)
        is_flag = n == flag_day
        color = flag if is_flag else fill
        op = 0 if animated else 1
        out.append(
            f"<rect x='{x}' y='{y}' width='{cell}' height='{cell}' rx='{cell * 0.18:.0f}' fill='{empty}'/>"
            f"<g id='{uid}-d{n}' style='opacity:{op};transform-origin:{x + cell / 2}px {y + cell / 2}px'>"
            f"<rect x='{x}' y='{y}' width='{cell}' height='{cell}' rx='{cell * 0.18:.0f}' fill='{color}'/>"
            f"<text x='{x + cell / 2}' y='{y + cell * 0.64}' text-anchor='middle' "
            f"font-family='Source Sans 3, sans-serif' font-weight='900' font-size='{cell * 0.42:.0f}' "
            f"fill='{text}'>{'!' if is_flag else n}</text></g>"
        )
    out.append("</svg>")
    return "".join(out)
