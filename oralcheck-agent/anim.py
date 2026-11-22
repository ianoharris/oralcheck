"""
Animated reels in the OralCheck house style (anim/STYLE.md).

A scene is a page in anim/ that draws the stage as a pure function of time;
anim/house.js draws everything around it (chrome, captions, labels, the
readout, the end card). This module voices a script, times each line, renders
the page frame by frame and mixes the sound, reusing the reel pipeline's
voice, word alignment, sound effects and music.

    python anim.py gauze out.mp4      # 2D sample: why the dentist grabs your tongue
    python anim.py zoom out.mp4       # 3D sample: from the face to the cells

A script is a list of lines: {"key", "say", "eyebrow"}; the scene keys its
motion to the keys. The closing call to action is added for you.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import align
import reel2
import reel2d
import reel3d

log = logging.getLogger("oralcheck.anim")

HERE = Path(__file__).parent / "anim"
W, H, FPS = 1080, 1920, 30
MIN_LINE = 3.0
CTA_HOLD = 2.2
PLATES = "Illustration based on Z-Anatomy (CC BY-SA 4.0) and BodyParts3D (CC BY-SA 2.1 JP). Shared under CC BY-SA 4.0."

# The formats test (Ian, 20 Nov 2026: "all those videos look the same"). One
# named series across four formats; the name is Ian's to pick.
SERIES = "Mouth Notes"

SCRIPTS = {
    # NIDCR, "The Oral Cancer Exam" (NIH Pub. 20-5032), step 6; topics.py tongue_sides.
    "gauze": dict(
        lines=[
            {"key": "hook", "say": "Ever wonder why your dentist grabs your tongue with gauze?", "eyebrow": "The oral cancer exam"},
            {"key": "exam", "say": "It is one step of a routine oral cancer exam.", "eyebrow": "The oral cancer exam"},
            {"key": "pull", "say": "With the gauze, they gently pull it to one side, then the other.", "eyebrow": "Step 6 · gauze"},
            {"key": "why", "say": "The sides and underside of your tongue are the most common place for oral cancer to start.",
             "eyebrow": "Tongue · lateral border"},
            {"key": "hidden", "say": "From straight on, you can barely see them.", "eyebrow": "Tongue · front view"},
            {"key": "you", "say": "So at home, stick your tongue out and look at each side.", "eyebrow": "Your turn"},
        ],
        credit="Source: NIDCR, The Oral Cancer Exam (NIH Pub. 20-5032) · " + PLATES,
    ),
    # ACS, "What Are Oral Cavity and Oropharyngeal Cancers?": almost all are squamous cell
    # carcinomas; squamous cells are the flat, thin cells that line the mouth and throat.
    "zoom": dict(
        lines=[
            {"key": "hook", "say": "Let's zoom from your jaw to the cells where almost every oral cancer starts.", "eyebrow": "Jaw · teeth · tongue"},
            {"key": "tongue", "say": "The side of the tongue, one of the most common places it begins.", "eyebrow": "Tongue · side"},
            {"key": "lining", "say": "Closer, the surface is a lining, many cells deep.", "eyebrow": "Lining · cut in section"},
            {"key": "cells", "say": "Its cells are called squamous cells. Near the surface, they are flat and thin.", "eyebrow": "Squamous cells"},
            {"key": "start", "say": "Almost all oral cancers start in these cells.", "eyebrow": "Where it starts"},
            {"key": "mirror", "say": "And that lining is the surface you can see in a mirror.", "eyebrow": "Back out"},
        ],
        credit="Source: American Cancer Society, What Are Oral Cavity and Oropharyngeal Cancers? · "
               "3D anatomy: Z-Anatomy (CC BY-SA 4.0), from BodyParts3D, DBCLS · Cells: illustration, not to scale in number",
    ),
    # Format sample: guess, then reveal. topics.py canker_vs_cancer, wipe_test, red_patch.
    "quiz": dict(
        lines=[
            {"key": "hook", "say": "Three spots in a mouth. Only one is a reason to book a dentist now.", "eyebrow": "Guess"},
            {"key": "optA", "say": "A: a painful, round sore, three days old.", "eyebrow": "A"},
            {"key": "optB", "say": "B: a white coating that wipes away.", "eyebrow": "B"},
            {"key": "optC", "say": "C: a red patch that does not hurt, there for three weeks.", "eyebrow": "C"},
            {"key": "count", "say": "Comment your letter. Three, two, one.", "eyebrow": "Your guess"},
            {"key": "answer", "say": "It is C. A red patch that will not go away is the most concerning thing you can find.", "eyebrow": "The answer"},
            {"key": "why", "say": "A canker sore heals in one to two weeks. Thrush wipes off. That red patch did neither.", "eyebrow": "Why"},
        ],
        credit="Sources: NHS, mouth ulcers; oralcheck.org/learn/white-and-red-patches · " + PLATES,
        foot="Illustration for education, not real cases. Not reviewed by a clinician.", foot_on=["optA", "optB", "optC", "answer", "why"],
        series={"name": SERIES, "ep": "Guess · 01"},
    ),
    # Format sample: levels. Figures as the screener states them (messages/en.json,
    # Questions.alcohol / tobacco / betel): Bagnardi 2015, Gandini 2008, IARC 85, Hashibe 2009.
    "levels": dict(
        lines=[
            {"key": "hook", "say": "Five habits, ranked by how much they multiply your risk of oral cancer.", "eyebrow": "Ranked"},
            {"key": "l1", "say": "Level one: moderate drinking. Nearly double the risk.", "eyebrow": "Level 1"},
            {"key": "l2", "say": "Level two: smoking every day. Two to six times.", "eyebrow": "Level 2"},
            {"key": "l3", "say": "Level three: heavy drinking, more than about four a day. About five times.", "eyebrow": "Level 3"},
            {"key": "l4", "say": "Level four: betel quid, paan or gutka. Seven to ten times, even without tobacco.", "eyebrow": "Level 4"},
            {"key": "l5", "say": "Level five: heavy smoking and heavy drinking together. About fifteen times.", "eyebrow": "Level 5"},
            {"key": "down", "say": "The good news: every level comes down when you cut back or quit.", "eyebrow": "The way down"},
        ],
        credit="Sources: Bagnardi et al. 2015; Gandini et al. 2008; IARC Monograph 85; Hashibe et al. 2009. "
               "Compared with people who do neither; ranges overlap.",
        series={"name": SERIES, "ep": "Ranked · 01"},
    ),
    # Format sample: how it works. topics.py hpv_is_common, throat_hpv_site, hpv_vaccine.
    "hpvclear": dict(
        lines=[
            {"key": "hook", "say": "Most adults catch HPV. Almost none get cancer from it. Here is why.", "eyebrow": "How it works"},
            {"key": "site", "say": "HPV-related throat cancers start at the tonsils and the base of the tongue.", "eyebrow": "Tonsils · base of tongue"},
            {"key": "land", "say": "When the virus reaches the cells lining this area, the body usually deals with it.", "eyebrow": "Lining cells"},
            {"key": "clear", "say": "Most infections clear on their own, without a single symptom.", "eyebrow": "Most clear"},
            {"key": "stay", "say": "Rarely, a type like HPV-16 stays, and changes a cell's DNA.", "eyebrow": "A few stay"},
            {"key": "vax", "say": "Gardasil 9 protects against HPV-16. It works best before exposure.", "eyebrow": "Prevention"},
        ],
        credit="Sources: CDC, HPV and cancer; CDC, HPV Vaccination Considerations · Cells and virus: illustration, not to scale · " + PLATES,
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["land", "clear", "stay", "vax"],
        series={"name": SERIES, "ep": "How it works · 01"},
    ),
    # Format sample: silent text story, no voice. topics.py canker_vs_cancer, painless,
    # wipe_test, lookalikes, two_week_rule. `len` is each card's time on screen.
    "silent": dict(
        silent=True,
        lines=[
            {"key": "hook", "say": "Before you google that spot in your mouth. Ask four things first.", "len": 3.4},
            {"key": "q1", "say": "Does it hurt? Canker sores usually do. Early cancer often does not.", "len": 4.2},
            {"key": "q2", "say": "Does it wipe off? Thrush wipes away. A patch that stays put does not.", "len": 4.2},
            {"key": "q3", "say": "Is there a cause? A sharp tooth, a burn, a bite: those settle once the cause is gone.", "len": 4.6},
            {"key": "q4", "say": "Has it been there two weeks? Then it is worth a dentist's look, whatever it is.", "len": 4.4},
            {"key": "cta", "say": "", "len": 3.6},
        ],
        credit="Sources: NHS, mouth ulcers; oralcheck.org/learn",
        series={"name": SERIES, "ep": "Read it · 01"},
    ),
    # Mouth Notes ep. 3 (docs/MOUTH_NOTES.md). ACS; NCI, What Is Cancer?; topics.py tongue_sides.
    "powers": dict(
        lines=[
            {"key": "hook", "say": "Let's zoom from your smile to a single strand of DNA.", "eyebrow": "Powers of ten"},
            {"key": "x10", "say": "Ten times closer: the side of the tongue, the most common place it starts.", "eyebrow": "×10"},
            {"key": "x100", "say": "A hundred times: the surface is a lining, many cells deep.", "eyebrow": "×100"},
            {"key": "x1000", "say": "A thousand times: one cell from the lining. Almost all oral cancers start in this lining.", "eyebrow": "×1,000"},
            {"key": "x10000", "say": "Ten thousand times: the nucleus, where the cell keeps its DNA.", "eyebrow": "×10,000"},
            {"key": "dna", "say": "Cancer starts when changes to that DNA let a cell stop following the rules.", "eyebrow": "DNA"},
        ],
        credit="Sources: American Cancer Society, What Are Oral Cavity and Oropharyngeal Cancers?; NCI, What Is Cancer? · "
               "Lining, cell, nucleus and DNA: illustration, not to scale · " + PLATES,
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["x10", "x100", "x1000", "x10000", "dna"],
        series={"name": SERIES, "ep": "How it works · 02"},
    ),
    # Mouth Notes ep. 5 (docs/MOUTH_NOTES.md). StatPearls NBK572115; NCI, What Is Cancer?
    "lifecell": dict(
        lines=[
            {"key": "hook", "say": "Your cheek lining replaces itself about every two weeks.", "eyebrow": "Life of a mouth cell"},
            {"key": "born", "say": "New cells are made in the bottom layer.", "eyebrow": "Basal layer"},
            {"key": "rise", "say": "They rise, flatten out, and are shed at the surface.", "eyebrow": "Rise and shed"},
            {"key": "damage", "say": "When a cell's DNA is damaged, it can keep dividing instead of moving on.", "eyebrow": "A damaged cell"},
            {"key": "patch", "say": "Enough of them can build into a growth you can see or feel.", "eyebrow": "A growth"},
        ],
        credit="Sources: StatPearls, Histology, Oral Mucosa (NCBI Bookshelf NBK572115); NCI, What Is Cancer? · Illustration, not to scale; the conveyor is sped up",
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["born", "rise", "damage", "patch"],
        series={"name": SERIES, "ep": "How it works · 03"},
    ),
    # Mouth Notes ep. 7 (docs/MOUTH_NOTES.md). NCI Dictionary: oral epithelial dysplasia; invasive cancer.
    "microscope": dict(
        lines=[
            {"key": "hook", "say": "What does a biopsy actually look for? Layers.", "eyebrow": "Under the microscope"},
            {"key": "normal", "say": "Normal lining: new cells at the bottom, flat ones on top, in order.", "eyebrow": "Normal"},
            {"key": "mild", "say": "Mild dysplasia: abnormal cells, only in the lowest layers.", "eyebrow": "Mild"},
            {"key": "severe", "say": "Moderate, then severe: they climb higher.", "eyebrow": "Moderate, severe"},
            {"key": "cancer", "say": "Cancer: they break through the floor, into the tissue beneath.", "eyebrow": "Invasive"},
            {"key": "worth", "say": "Dysplasia is not cancer, but it can become cancer. That is why it is worth finding.", "eyebrow": "Why it matters"},
        ],
        credit="Sources: NCI Dictionary of Cancer Terms, oral epithelial dysplasia and invasive cancer; grading by thirds of the lining (WHO) · Illustration, not a real slide",
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["normal", "mild", "severe", "cancer", "worth"],
        series={"name": SERIES, "ep": "How it works · 04"},
    ),
    # Mouth Notes ep. 8. Hecht, Nat Rev Cancer 2003; topics.py quitting.
    "tobaccodna": dict(
        lines=[
            {"key": "hook", "say": "Tobacco carries dozens of cancer-causing chemicals. Here is what they do.", "eyebrow": "How it works"},
            {"key": "stick", "say": "In the cells lining your mouth, some of them stick to DNA.", "eyebrow": "Adducts"},
            {"key": "repair", "say": "The cell's repair systems fix most of that damage.", "eyebrow": "Repair"},
            {"key": "slip", "say": "Not all of it. A mistake that slips through can switch off a gene that stops tumours.", "eyebrow": "A mistake"},
            {"key": "quit", "say": "Quit, and the risk drops measurably within a few years.", "eyebrow": "Quitting"},
        ],
        credit="Sources: Hecht, Nature Reviews Cancer 2003, tobacco carcinogens and DNA adducts; oralcheck.org prevention · Illustration, not to scale",
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["stick", "repair", "slip"],
        series={"name": SERIES, "ep": "How it works · 05"},
    ),
    # Mouth Notes ep. 9. IARC Monograph 90; buccal cell cytomorphometry (Asian J Med Sci 2023); topics.py hpv_is_common.
    "sized": dict(
        lines=[
            {"key": "hook", "say": "How small is HPV? Let's shrink.", "eyebrow": "Sized"},
            {"key": "rice", "say": "Start with a grain of rice.", "eyebrow": "Rice"},
            {"key": "cell", "say": "One cell from your cheek: about a twentieth of a millimetre.", "eyebrow": "A cheek cell"},
            {"key": "hpv", "say": "HPV: about fifty-five nanometres. Nearly a thousand would fit across that one cell.", "eyebrow": "HPV"},
            {"key": "clear", "say": "Far too small to see, and most of the time the body clears it anyway.", "eyebrow": "Most clear"},
        ],
        credit="Sources: IARC Monograph 90 (HPV about 55 nm); normal buccal cell diameter about 49.5 µm (Asian Journal of Medical Sciences, 2023); CDC · Illustration",
        series={"name": SERIES, "ep": "Sized · 01"},
    ),
    # Mouth Notes ep. 10. StatPearls: sublingual gland; mylohyoid; topics.py floor_of_mouth, painless.
    "cutaway": dict(
        lines=[
            {"key": "hook", "say": "What is under your tongue? Let's peel it back.", "eyebrow": "Cutaway"},
            {"key": "lining", "say": "First, the lining: thin, smooth, and where oral cancer starts.", "eyebrow": "Layer 1"},
            {"key": "gland", "say": "Under it, a salivary gland, and the nerve that gives your tongue feeling.", "eyebrow": "Layer 2"},
            {"key": "muscle", "say": "Then the muscle that forms the floor of your mouth.", "eyebrow": "Layer 3"},
            {"key": "pain", "say": "Pain usually starts only when a growth reaches a nerve or breaks open, so early changes often do not hurt.", "eyebrow": "Why it is quiet"},
            {"key": "look", "say": "Lift your tongue and look at the floor of your mouth once a month.", "eyebrow": "Your turn"},
        ],
        credit="Sources: StatPearls, Anatomy, Sublingual Gland; StatPearls, Mylohyoid; oralcheck.org/learn · Schematic, not to scale",
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["lining", "gland", "muscle", "pain"],
        series={"name": SERIES, "ep": "Cutaway · 01"},
    ),
    # Mouth Notes ep. 11. topics.py canker_vs_cancer, wipe_test, red_patch, neck_lump, white_patch.
    "thisorthat": dict(
        lines=[
            {"key": "hook", "say": "Five rounds. Worry or wait? Answer before the reveal.", "eyebrow": "This or that"},
            {"key": "r1", "say": "A sore that hurts, and is shrinking after a week? Wait.", "eyebrow": "Round 1"},
            {"key": "r2", "say": "A white coating that wipes off? Usually thrush, not cancer.", "eyebrow": "Round 2"},
            {"key": "r3", "say": "A painless red patch, three weeks old? Get it checked.", "eyebrow": "Round 3"},
            {"key": "r4", "say": "A lump in your neck for a month, with no cold? Get it checked.", "eyebrow": "Round 4"},
            {"key": "r5", "say": "A white patch that will not rub off? Get it checked.", "eyebrow": "Round 5"},
        ],
        credit="Sources: NHS, mouth ulcers; oralcheck.org/learn · " + PLATES,
        foot="Illustrations for education, not real cases. Not reviewed by a clinician.", foot_on=["r1", "r2", "r3", "r4", "r5"],
        series={"name": SERIES, "ep": "This or that · 01"},
    ),
    # Mouth Notes ep. 12. topics.py throat_hpv_site, hpv_throat_symptoms.
    "myth": dict(
        lines=[
            {"key": "hook", "say": "Myth: if the mirror shows nothing, there is nothing there.", "eyebrow": "Myth"},
            {"key": "where", "say": "Some oral cancers start where a mirror cannot reach: the base of the tongue and the tonsils.", "eyebrow": "Out of reach"},
            {"key": "nothing", "say": "There is often nothing to see at all.", "eyebrow": "Nothing visible"},
            {"key": "signs", "say": "The signs are different: a sore throat that lasts, a lump in the neck, ear pain on one side.", "eyebrow": "The signs"},
            {"key": "check", "say": "Any of those for more than two weeks gets checked.", "eyebrow": "Two weeks"},
        ],
        credit="Sources: oralcheck.org/learn (HPV-related throat cancer) · " + PLATES,
        series={"name": SERIES, "ep": "Myth · 01"},
    ),
    # Mouth Notes, 3D lane prototype (22 Nov 2026). NCI, Preventing Cervical Cancer: The Development of HPV Vaccines.
    "vlp": dict(
        blender="vlp",
        lines=[
            {"key": "hook", "say": "The HPV vaccine is a virus with nothing inside.", "eyebrow": "How it works"},
            {"key": "real", "say": "A real HPV is a shell of seventy-two parts, wrapped around its DNA.", "eyebrow": "Real HPV"},
            {"key": "build", "say": "Scientists found the shell protein can build that shell by itself, with no virus at all.", "eyebrow": "L1 protein"},
            {"key": "empty", "say": "The copy is empty. No DNA, so it cannot infect anyone.", "eyebrow": "Virus-like particle"},
            {"key": "immune", "say": "Your immune system learns its shape and makes antibodies that fit it.", "eyebrow": "Antibodies"},
            {"key": "later", "say": "If real HPV ever shows up, those antibodies are already waiting.", "eyebrow": "Protected"},
        ],
        labels={"real": {"k": "Inside", "t": "Its DNA", "d": "what makes it a virus", "x": 540, "y": 500, "side": "right"},
                "empty": {"k": "Inside", "t": "Nothing", "d": "no viral DNA", "x": 540, "y": 500, "side": "right"},
                "immune": {"k": "Y-shaped", "t": "Antibodies", "d": "they fit the shell", "x": 700, "y": 330, "side": "right"}},
        readouts={"real": ["72", "parts in the shell"], "build": ["360", "copies of one protein, L1"]},
        credit="Sources: National Cancer Institute, Preventing Cervical Cancer: The Development of HPV Vaccines; CDC · Stylized 3D, not to scale",
        foot="Illustration for education. Not reviewed by a clinician.", foot_on=["real", "build", "empty", "immune", "later"],
        series={"name": SERIES, "ep": "How it works · 06"},
    ),
    # Mouth Notes, math lane prototype (22 Nov 2026). CDC, Benefits of Quitting Smoking.
    "quit": dict(
        manim=("quit.py", "Quit"),
        lines=[
            {"key": "hook", "say": "Quit smoking, and your risk of mouth cancer starts to fall. Here is the curve.", "eyebrow": "Quitting"},
            {"key": "axes", "say": "Start with the extra risk smoking adds, on the day you quit.", "eyebrow": "Day one"},
            {"key": "half", "say": "Five to ten years later, that extra risk has dropped by half.", "eyebrow": "5 to 10 years"},
            {"key": "twenty", "say": "By twenty years, it is close to someone who never smoked.", "eyebrow": "20 years"},
            {"key": "never", "say": "It is never too late for it to count.", "eyebrow": "Never too late"},
        ],
        credit="Source: CDC, Benefits of Quitting Smoking (mouth, throat and voice box cancers) · Curve shape between the CDC's points is illustrative",
        series={"name": SERIES, "ep": "The math · 01"},
    ),
    # Calendar 19 Nov 2026 (Ian's redo of the age carousel). SEER_BY_AGE and
    # newCaseShareByAge in src/lib/seerStats.ts: SEER 21, 2019 to 2023.
    "age": dict(
        lines=[
            {"key": "hook", "say": "How common is oral cancer at 25? At 45? At 65?", "eyebrow": "Oral cancer by age"},
            {"key": "at25", "say": "At 25, it is rare: about one new case per 100,000 people a year.", "eyebrow": "Age 25 to 29"},
            {"key": "double", "say": "From there, the rate roughly doubles every five years, into your fifties.", "eyebrow": "Age 30 to 54"},
            {"key": "by65", "say": "By 65, it is about 45 per 100,000, and it peaks near 51.", "eyebrow": "Age 65 and up"},
            {"key": "share", "say": "Ninety-four of every hundred new cases are in people 45 and older.", "eyebrow": "Share of new cases"},
            {"key": "any", "say": "But rare is not zero. A sore that lasts two weeks needs a look, at any age.", "eyebrow": "At any age"},
        ],
        credit="Source: National Cancer Institute, SEER*Explorer and Cancer Stat Facts, SEER 21, 2019 to 2023. "
               "Rates per 100,000 people a year, in five-year age groups",
    ),
    # Calendar 1 Dec 2026 (Ian's redo of the Gardasil image). topics.py
    # hpv_vaccine; CDC, HPV Vaccination Considerations, checked 5 Nov 2026.
    "hpvvax": dict(
        lines=[
            {"key": "hook", "say": "The HPV vaccine works best before exposure. But it is still available after.", "eyebrow": "The HPV vaccine"},
            {"key": "range", "say": "Gardasil 9 is approved from age 9 through 45.", "eyebrow": "Who can get it"},
            {"key": "strains", "say": "It protects against HPV 16 and 18, the types behind most HPV-related cancers.", "eyebrow": "What it covers"},
            {"key": "routine", "say": "It is recommended at 11 or 12, ideally before any exposure.", "eyebrow": "The best time"},
            {"key": "adults", "say": "Through 26, catch-up is recommended. From 27 to 45, ask your clinician.", "eyebrow": "If you missed it"},
            {"key": "limits", "say": "It prevents new infections. It cannot treat one you already have.", "eyebrow": "What it cannot do"},
        ],
        credit="Source: CDC, HPV Vaccination Considerations",
    ),
}


def milestone_spec(d: dict) -> dict:
    """The 1,000-visitor reel, written around the numbers /api/reach returns the
    day it renders (milestone.py). Nothing here is typed by hand."""
    finished = int(round(d["finished"] / 10.0) * 10)
    return dict(
        lines=[
            {"key": "hook", "say": "A thousand people have now visited OralCheck.", "eyebrow": "1,000"},
            {"key": "where", "say": f"They came from {d['countries']} countries and {d['states']} states.", "eyebrow": "Where"},
            {"key": "finished", "say": f"About {finished} of them made it all the way to a result.", "eyebrow": "Finished"},
            {"key": "question", "say": "The question that brought the most people here from search: is this a canker sore, or something worse?",
             "eyebrow": "Most searched"},
            {"key": "answer", "say": "The answer is time. A sore that hasn't healed in two weeks needs a dentist.", "eyebrow": "The answer"},
            {"key": "thanks", "say": "Thank you for checking, and for sending it on.", "eyebrow": "Thank you"},
        ],
        credit="Counts: Google Analytics for oralcheck.org, a floor, since some visits are never counted",
        data={"users": max(1000, int(d["users"])), "countries": d["countries"], "states": d["states"], "finished": finished},
    )


CTA = {"key": "cta", "say": "Check your own risk, free, at oralcheck.org.", "eyebrow": ""}


def _page(scene: str) -> str:
    html = (HERE / f"{scene}.html").read_text()
    if "<!--PLATE_A-->" in html:
        html = html.replace("<!--PLATE_A-->", reel2d._scoped((reel2d.HERE / "plate_a.svg").read_text(), "a-"))
    if "<!--PLATE_B-->" in html:
        html = html.replace("<!--PLATE_B-->", reel2d._scoped((reel2d.HERE / "plate_b.svg").read_text(), "b-"))
    return html


def _serve(scene: str):
    def serve(route):
        name = route.request.url.split("anim.local/", 1)[1].split("?")[0]
        if name == "scene.html":
            return route.fulfill(status=200, body=_page(scene), headers={"Content-Type": "text/html"})
        for d in (HERE, reel3d.HERE):   # fonts, three.js and the 3D model are shared with reel3d
            if (d / name).exists():
                path = d / name
                break
        else:
            return route.fulfill(status=404, body="")
        ctype = {".css": "text/css", ".js": "text/javascript", ".ttf": "font/ttf", ".glb": "model/gltf-binary",
                 ".png": "image/png", ".jpg": "image/jpeg"}.get(path.suffix, "application/octet-stream")
        route.fulfill(status=200, body=path.read_bytes(), headers={"Content-Type": ctype})
    return serve


def render(scene: str, plan: dict, total: float, out_mp4: str, fps: int = FPS) -> None:
    from playwright.sync_api import sync_playwright

    n = int(round(total * fps))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
                           "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                           "-r", str(fps), out_mp4], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": W, "height": H})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)[:300]))
        page.on("console", lambda m: errors.append(m.text[:300]) if m.type == "error" else None)
        page.route("http://anim.local/**", _serve(scene))
        page.add_init_script(f"window.PLAN = {json.dumps(plan)};")
        page.goto("http://anim.local/scene.html")
        try:
            page.wait_for_function("window.render && window.render(0)", timeout=180000)
        except Exception as exc:
            raise RuntimeError(f"scene {scene} never became ready ({exc}); page errors: {errors[:5]}") from None
        page.evaluate("async () => { await document.fonts.ready; }")
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"window.render({i / fps})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=92, timeout=300000))
            if i % 150 == 0:
                log.info("%s frame %d/%d (%.0fs)", scene, i, n, time.time() - t0)
        if errors:
            log.warning("page errors: %s", errors[:5])
        browser.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg failed encoding frames")


def build(scene: str, out_path: str, *, tts, music: str | None = None, workdir: str | None = None,
          spec: dict | None = None) -> str:
    spec = spec or SCRIPTS[scene]
    lines = spec["lines"] + [CTA]
    workdir = workdir or tempfile.mkdtemp(prefix=f"anim_{scene}_")
    wavs = [tts(l["say"]) for l in lines]
    speech = [reel2._duration(w) / reel2.VOICE_TEMPO for w in wavs]
    pads = [reel2.GAP + (CTA_HOLD if l["key"] == "cta" else max(0.0, MIN_LINE - d)) for l, d in zip(lines, speech)]
    voice = reel2._voice_track(wavs, pads, workdir)
    t, windows, timing = 0.0, [], []
    for d, pad, l in zip(speech, pads, lines):
        windows.append((t, t + d, l["say"]))
        timing.append((t, d + pad))
        t += d + pad
    total = t
    words = align.align(voice, windows)
    shots = [{"key": l["key"], "eyebrow": l["eyebrow"], "t0": round(t0, 3), "len": round(n, 3), "words": w}
             for l, (t0, n), w in zip(lines, timing, words)]
    plan = {"shots": shots, "cta_t0": shots[-1]["t0"], "credit": spec["credit"], "foot": spec.get("foot", ""),
            "foot_on": spec.get("foot_on", []), "data": spec.get("data", {}), "series": spec.get("series")}
    events = [("glide", max(0.0, s["t0"] - 0.15)) for s in shots[1:]] + [("settle", shots[-1]["t0"] + 0.1)]
    video = os.path.join(workdir, "video.mp4")
    page = scene
    if spec.get("blender"):
        # 3D lane: Blender renders the stage band keyed to these timings, bg3d.html frames it
        fdir = HERE / "_frames" / scene
        if fdir.exists():
            for f in fdir.glob("f*.png"):
                f.unlink()
        fdir.mkdir(parents=True, exist_ok=True)
        pj = os.path.join(workdir, "plan3d.json")
        Path(pj).write_text(json.dumps({**plan, "total": total}))
        subprocess.run(["blender", "-b", "--factory-startup", "-P", str(Path(__file__).parent / "blender" / f"{spec['blender']}.py"),
                        "--", pj, str(fdir) + "/"], check=True, stdout=subprocess.DEVNULL)
        plan.update(frames=f"_frames/{scene}", frames_n=len(list(fdir.glob("f*.png"))),
                    labels=spec.get("labels", {}), readouts=spec.get("readouts", {}))
        page = "bg3d"
    elif spec.get("manim"):
        # math lane: Manim renders the stage band keyed to these timings; frames extracted for bg3d.html
        fdir = HERE / "_frames" / scene
        if fdir.exists():
            for f in fdir.glob("f*.png"):
                f.unlink()
        fdir.mkdir(parents=True, exist_ok=True)
        pj = os.path.join(workdir, "plan2d.json")
        Path(pj).write_text(json.dumps({**plan, "total": total}))
        mfile, mscene = spec["manim"]
        subprocess.run(["manim", "-r", "1080,1000", "--fps", "30", "--media_dir", workdir, "-o", "m.mp4",
                        str(Path(__file__).parent / "manim" / mfile), mscene],
                       check=True, env={**os.environ, "MN_PLAN": pj}, stdout=subprocess.DEVNULL)
        mp4 = next(Path(workdir).rglob("m.mp4"))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf", "fps=30", str(fdir / "f%04d.png")], check=True)
        plan.update(frames=f"_frames/{scene}", frames_n=len(list(fdir.glob("f*.png"))),
                    labels=spec.get("labels", {}), readouts=spec.get("readouts", {}))
        page = "bg3d"
    render(page, plan, total, video)
    audio = reel2._final_audio(voice, reel3d._sfx_track(events, total, workdir), music, total, workdir)
    reel2._run(["ffmpeg", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    (Path(out_path).with_suffix(".json")).write_text(json.dumps(plan, indent=1))
    log.info("%s: %.1fs -> %s", scene, total, out_path)
    return out_path


def build_silent(scene: str, out_path: str, *, music: str | None, workdir: str | None = None) -> str:
    """A reel with no voice (spec `silent`): each line holds for its `len`, the
    scene draws all the text, and the sound is the music bed plus the glide on
    each cut, mixed to the same loudness as the voiced reels."""
    spec = SCRIPTS[scene]
    workdir = workdir or tempfile.mkdtemp(prefix=f"anim_{scene}_")
    t, shots = 0.0, []
    for l in spec["lines"]:
        shots.append({"key": l["key"], "eyebrow": l.get("eyebrow", ""), "t0": round(t, 3), "len": l["len"], "words": []})
        t += l["len"]
    total = t
    plan = {"shots": shots, "cta_t0": shots[-1]["t0"], "credit": spec["credit"], "foot": spec.get("foot", ""),
            "foot_on": spec.get("foot_on", []), "data": spec.get("data", {}), "series": spec.get("series")}
    video = os.path.join(workdir, "video.mp4")
    render(scene, plan, total, video)
    events = [("glide", max(0.0, s["t0"] - 0.15)) for s in shots[1:]] + [("settle", shots[-1]["t0"] + 0.1)]
    sfx = reel3d._sfx_track(events, total, workdir)
    inputs = ["-i", sfx] + (["-i", music] if music else [])
    mix = "[0:a][1:a]amix=inputs=2:duration=first:weights='0.5 1'" if music else "[0:a]anull"
    audio = os.path.join(workdir, "audio.m4a")
    reel2._run(["ffmpeg", "-y", *inputs, "-filter_complex",
                f"{mix},atrim=0:{total:.2f},afade=t=out:st={max(0, total - 1.2):.2f}:d=1.2,loudnorm=I=-14:TP=-1.5[a]",
                "-map", "[a]", "-c:a", "aac", "-b:a", "192k", audio])
    reel2._run(["ffmpeg", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
                "-shortest", "-movflags", "+faststart", out_path])
    (Path(out_path).with_suffix(".json")).write_text(json.dumps(plan, indent=1))
    log.info("%s (silent): %.1fs -> %s", scene, total, out_path)
    return out_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    import oralcheck_agent as A
    scene, out = sys.argv[1], sys.argv[2]
    music = A._generate_music_bed(40, f"anim-{scene}")
    if music is None and A.REEL_MUSIC.exists():
        music = A._loop_music_seamless(str(A.REEL_MUSIC), 42)
    if SCRIPTS.get(scene, {}).get("silent"):
        build_silent(scene, out, music=music)
    else:
        build(scene, out, tts=A._fal_tts, music=music)
