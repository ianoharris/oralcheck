"""
What a post is about, what shape it takes, and how it opens.

The idea generator used to pick all three itself, every week, and left to its
own judgement it chose the same five or six subjects (survival by stage, HPV
overtaking tobacco, the yearly case count, "your dentist checks more than
teeth") and wrote them in the same grammar ("X. Y.", "Most people don't know").
Thirty-eight ideas in, the feed read like one post rephrased.

So the choosing moves here, into code. Each weekly slot is assigned:

  - a topic from TOPICS, the least recently used one that suits the shape
  - a shape from SHAPES, the least recently used one for that format
  - a hook style from HOOKS, never repeated within a batch

and the model's job narrows to writing that one idea well. Variety then comes
from the rotation rather than from asking nicely.

Every fact in TOPICS is taken from the site's own learn pages (messages/en.json)
or from src/lib/seerStats.ts, and names the page it came from. A post can only
claim what the site already says. When a page changes, change its topic here.
"""
from __future__ import annotations

import random
import re
from datetime import datetime, timezone

# ── topics ────────────────────────────────────────────────────────────────────
# tags say which shapes a topic can carry:
#   sign     something you can see or feel        steps    a procedure to follow
#   site     a place in the mouth (has a zone)    pair     two things to tell apart
#   stat     built on a figure from seerStats.ts  list     several parallel items
#   myth     corrects a common belief             photo    a licensed clinical photo exists
#   timeline the two-week rule applies to it      care     about getting checked
# zone is an art.ZONES key for the mouth-map visuals; photo is a signPhotos key.

TOPICS: dict[str, dict] = {
    # where it starts
    "tongue_sides": dict(
        pillar="self_exam", page="/learn/signs", zone="tongue",
        tags={"site", "sign", "steps"},
        kw=("side of the tongue", "sides of the tongue", "underside"),
        facts=["The sides and underside of the tongue are the most common site for oral cancer overall.",
               "It is easy to overlook without a self-exam: you have to stick your tongue out and look at each side."]),
    "floor_of_mouth": dict(
        pillar="self_exam", page="/learn/signs", zone="floor",
        tags={"site", "sign", "steps"},
        kw=("floor of the mouth", "under the tongue", "under your tongue"),
        facts=["The floor of the mouth, the U-shaped tissue under the tongue, is one of the highest-risk sites.",
               "It is hard to see without lifting the tongue to the roof of the mouth.",
               "A small tumor here may grow for months before causing any discomfort."]),
    "lower_lip_sun": dict(
        pillar="self_exam", page="/learn/prevention", zone="lips",
        tags={"site", "sign", "myth"},
        kw=("lip", "sun", "spf", "uv"),
        facts=["Chronic sun exposure is a leading risk factor for cancer of the lower lip, not for cancers inside the mouth.",
               "The lower lip is the most common lip site. People who work outdoors are at higher risk.",
               "SPF lip balm and a wide-brimmed hat offer meaningful protection."]),
    "gums_mimic": dict(
        pillar="self_exam", page="/learn/signs", zone="gums",
        tags={"site", "sign", "myth"},
        kw=("gum", "gingiva", "loose teeth"),
        facts=["Cancer of the gums can mimic gum disease.",
               "Loose teeth without a dental cause is a key clue."]),
    "throat_hpv_site": dict(
        pillar="hpv_connection", page="/learn/hpv", zone="throat",
        tags={"site", "sign"},
        kw=("tonsil", "base of the tongue", "oropharynx", "oropharyngeal"),
        facts=["HPV-related cancers tend to start at the base of the tongue and the tonsils, the oropharynx.",
               "There is often no visible lesion, and the area is hard to see in a mirror.",
               "That is why these cancers are frequently caught later than other oral cancers."]),

    # what it looks like
    "red_patch": dict(
        pillar="self_exam", page="/learn/white-and-red-patches", zone="cheeks",
        tags={"sign", "myth"},
        kw=("red patch", "erythroplakia"),
        facts=["A persistent red patch (erythroplakia) is the single most concerning thing you can find in your own mouth.",
               "It is far less common than a white patch. Studies estimate 50% or more of red patches are already cancerous or precancerous at biopsy.",
               "It is also the easiest to dismiss: it does not hurt and does not look dramatic."]),
    "white_patch": dict(
        pillar="self_exam", page="/learn/white-and-red-patches", zone="cheeks", photo="white",
        tags={"sign", "photo"},
        kw=("white patch", "leukoplakia"),
        facts=["Leukoplakia is a white patch that cannot be scraped off and cannot be explained by anything else.",
               "It is a description, not a diagnosis. Most are benign, but roughly 5 to 17% become malignant if left untreated.",
               "It is usually painless, which is why it goes unnoticed for months."]),
    "speckled_patch": dict(
        pillar="self_exam", page="/learn/white-and-red-patches", zone="cheeks", photo="mixed",
        tags={"sign", "photo"},
        kw=("speckled", "red and white", "erythroleukoplakia", "mixed patch"),
        facts=["A mixed red-and-white speckled patch carries the highest risk of all patch types.",
               "The defining feature of a worrying patch is that it does not rub or scrape off."]),
    "wipe_test": dict(
        pillar="self_exam", page="/learn/white-and-red-patches",
        tags={"pair", "sign"},
        kw=("thrush", "wipes away", "wipe away", "scrape off"),
        facts=["Oral thrush is a yeast infection, and the giveaway is that it wipes away, often leaving a red sore area underneath.",
               "A leukoplakia patch stays put when you try to rub it away.",
               "Neither can be confirmed by eye. A patch that stays for two weeks gets checked."]),
    "lookalikes": dict(
        pillar="self_exam", page="/learn/white-and-red-patches",
        tags={"list", "myth"},
        kw=("geographic tongue", "lichen planus", "frictional", "look scary", "harmless"),
        facts=["Plenty of alarming-looking things in the mouth are harmless:",
               "Frictional keratosis: a callus from a cheek you bite, a sharp tooth or a denture. Settles once the cause is removed.",
               "Oral thrush: a yeast infection that wipes away.",
               "Lichen planus: fine white lacy lines, usually on both cheeks at once.",
               "A burn from hot food or drink: alarming for a few days, then heals.",
               "Geographic tongue: smooth red areas with pale borders that move around the tongue over weeks. Harmless.",
               "What matters is anything new that is still there after two weeks."]),
    "canker_vs_cancer": dict(
        pillar="myth_busting", page="/learn/canker-sore-vs-oral-cancer",
        tags={"pair", "sign", "timeline"},
        kw=("canker",),
        facts=["A canker sore is round or oval with a white or yellow center and a red rim, and usually painful.",
               "Canker sores appear inside the mouth only, never on the outer lip, and heal on their own in 7 to 14 days.",
               "An oral cancer lesion is often painless early, has irregular, raised or hard edges, may bleed easily, and does not heal."]),
    "edges_and_bleeding": dict(
        pillar="self_exam", page="/learn/signs",
        tags={"sign", "list"},
        kw=("bleed", "hard edge", "raised edge", "indurated", "lump", "thickening"),
        facts=["Warning signs beyond colour: irregular, raised or hardened edges, a sore that bleeds easily when touched,",
               "and a new lump or thickening in the cheek, tongue, gum or floor of the mouth, often firm, like a pea under the skin."]),
    "painless": dict(
        pillar="myth_busting", page="/learn/signs",
        tags={"myth", "sign"},
        kw=("painless", "doesn't hurt", "does not hurt", "no pain"),
        facts=["Early oral cancer frequently does not hurt. Red and white patches are often completely painless.",
               "By the time pain appears, usually from nerve involvement or ulceration, the cancer is often more advanced.",
               "The absence of pain is not reassurance. It is why the two-week rule exists."]),
    "two_week_rule": dict(
        pillar="self_exam", page="/learn/signs",
        tags={"timeline", "sign"},
        kw=("two weeks", "2 weeks", "two-week", "three weeks", "heal"),
        facts=["Anything in the mouth that has not healed or gone away in two weeks should be looked at by a dentist or doctor.",
               "Canker sores and minor injuries heal within that window. Oral cancer lesions do not.",
               "What should prompt a visit: anything new, persistent, painless but unusual, or that bleeds easily."]),

    # HPV
    "neck_lump": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"sign", "myth", "timeline"},
        kw=("neck", "lymph node", "lump in the neck"),
        facts=["A painless lump in the neck is often the first sign of HPV-related throat cancer, caused by lymph node involvement.",
               "A swollen neck node that persists for more than 2 weeks without an obvious infection is worth getting checked."]),
    "hpv_throat_symptoms": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"list", "sign"},
        kw=("sore throat", "ear pain", "hoarse", "swallow", "voice"),
        facts=["HPV-related throat cancer symptoms: a sore throat that does not resolve in 2 weeks,",
               "a painless neck lump, food that feels like it is catching, ear pain on one side without an ear infection,",
               "hoarseness lasting more than two weeks, and unexplained weight loss."]),
    "hpv_overtook_tobacco": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"myth", "stat"},
        kw=("overtaken", "overtook", "leading cause", "300%"),
        facts=["HPV has overtaken tobacco as the leading cause of oropharyngeal cancers: the tonsils, base of tongue and back of the throat.",
               "Cases have risen by more than 300% since the 1980s.",
               "This is the throat, specifically. Tobacco is still the biggest driver of cancers in the mouth itself."]),
    "hpv_who": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"myth"},
        kw=("non-smoker", "nonsmoker", "never smoked", "40 and 60", "smoker's disease"),
        facts=["HPV-related throat cancer most commonly affects men between 40 and 60 with no history of tobacco use.",
               "That is what makes it easy to dismiss: people assume oral cancer is a smoker's disease."]),
    "hpv_is_common": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"myth"},
        kw=("most sexually active", "clear on their own", "common virus"),
        facts=["HPV is extremely common. Most sexually active adults have been exposed at some point.",
               "Most infections clear on their own without symptoms, and the vast majority never lead to cancer.",
               "Certain strains, especially HPV-16, can cause the DNA changes that lead to cancer in some people."]),
    "hpv_vaccine": dict(
        pillar="hpv_connection", page="/learn/hpv",
        tags={"myth", "care"},
        kw=("vaccine", "gardasil", "vaccinated"),
        facts=["Gardasil 9 protects against HPV-16 and HPV-18, the strains behind most HPV-related cancers.",
               "It is FDA-approved for ages 9 through 45 and most effective before exposure, which is why it is recommended for preteens.",
               "Adults who were not vaccinated earlier may still benefit: ask a doctor. It cannot treat an existing infection."]),

    # risk
    "tobacco_all_forms": dict(
        pillar="myth_busting", page="/learn/risk-factors",
        tags={"list", "myth"},
        kw=("vape", "vaping", "chew", "snuff", "cigar", "pipe", "tobacco"),
        facts=["Every form of tobacco raises oral cancer risk: cigarettes, cigars, pipes, chewing tobacco, snuff and vaping products.",
               "Tobacco is responsible for roughly 75% of traditional oral cavity cancers.",
               "Risk scales with how much and for how long."]),
    "quitting": dict(
        pillar="myth_busting", page="/learn/prevention",
        tags={"myth"},
        kw=("quit", "quitting", "stop smoking", "ex-smoker"),
        facts=["Tobacco is the single biggest modifiable risk factor for oral cancer.",
               "Risk drops measurably within a few years of quitting, and long-term ex-users approach the risk of people who never used tobacco.",
               "It is never too late for it to count."]),
    "alcohol": dict(
        pillar="myth_busting", page="/learn/risk-factors",
        tags={"myth"},
        kw=("alcohol", "drink", "drinking"),
        facts=["Alcohol is a direct carcinogen in the mouth, and risk rises with the amount.",
               "Heavy drinking, more than 3 to 4 drinks a day, carries the highest risk.",
               "Moderate levels (up to 1 drink a day for women, 2 for men) meaningfully lower risk compared to heavy use."]),
    "tobacco_plus_alcohol": dict(
        pillar="myth_busting", page="/learn/risk-factors",
        tags={"myth", "pair"},
        kw=("together", "combination", "multiplies", "synergistic", "15 times"),
        facts=["Tobacco and alcohol together do not add their risks, they multiply them.",
               "People who smoke more than a pack a day and have three or more drinks a day have about 15 times "
               "the oral cancer risk of people who do neither (a pooled analysis of 17 studies, Hashibe 2009).",
               "Both damage the same tissues, and alcohol may help tobacco carcinogens get into the cells lining the mouth.",
               "If you use both, cutting back on either one significantly lowers your risk."]),
    "betel_quid": dict(
        pillar="myth_busting", page="/screener",
        tags={"myth"},
        kw=("betel", "areca", "paan", "gutka"),
        facts=["Betel quid, with or without tobacco, is classed as a Group 1 carcinogen for oral cancer by the WHO's cancer agency (IARC).",
               "That includes areca nut, paan and gutka.",
               "It raises risk independently of tobacco, which is why the OralCheck screener asks about it."]),
    "cant_control": dict(
        pillar="screener_cta", page="/learn/prevention",
        tags={"list"},
        kw=("family history", "can't control", "cannot control", "age"),
        facts=["Age, sex, family history and immune status all affect oral cancer risk and cannot be changed.",
               "Having several of them is a reason to be more diligent about the ones you can control,",
               "and to talk to your dentist about how often you are screened."]),
    "men_vs_women": dict(
        pillar="stats", page="/learn/facts",
        tags={"stat"},
        kw=("men", "women", "2.6"),
        facts=["Men are diagnosed with oral cancer about 2.6 times as often as women (SEER age-adjusted incidence).",
               "HPV-related throat cancer most often affects men aged 40 to 60."]),
    "median_age": dict(
        pillar="stats", page="/learn/facts",
        tags={"stat", "myth"},
        kw=("median age", "65", "younger", "young adults"),
        facts=["The median age at diagnosis is 65 (SEER).",
               "But HPV-related throat cancers increasingly appear in middle-aged adults, so age alone should not rule out getting a symptom checked."]),

    # getting checked
    "dentist_screening": dict(
        pillar="screener_cta", page="/learn/prevention",
        tags={"care", "steps"},
        kw=("dentist", "dental", "checkup", "hygienist", "cleaning"),
        facts=["A routine dental visit includes a short oral cancer check of the lips, gums, tongue, cheeks, palate and throat.",
               "Most early-stage oral cancers are found this way.",
               "For people who skip dental care, cancers are more often caught at later stages, when outcomes are worse."]),
    "biopsy": dict(
        pillar="self_exam", page="/learn/white-and-red-patches",
        tags={"care", "steps", "myth"},
        kw=("biopsy",),
        facts=["Nobody can tell a harmless patch from a dangerous one by eye, not a clinician and not a photograph.",
               "The answer comes from a biopsy: a small sample, usually under local anaesthetic, looked at under a microscope.",
               "It sounds bigger than it is. It is a short appointment, and it is the only thing that turns a worry into an answer."]),
    "low_cost_care": dict(
        pillar="screener_cta", page="/find-care",
        tags={"care", "list"},
        kw=("insurance", "afford", "free clinic", "dental school", "community health"),
        facts=["No dentist, or no insurance, is not the end of the road.",
               "Community health centers (HRSA-funded) charge on a sliding scale, dental schools offer lower-cost care,",
               "and free clinics exist in many areas. oralcheck.org/find-care searches for them near you."]),
    "monthly_self_exam": dict(
        pillar="self_exam", page="/learn/self-exam", zone="tongue",
        tags={"steps", "site"},
        kw=("self-exam", "self exam", "check your mouth", "mirror", "once a month"),
        facts=["A self-exam takes a couple of minutes, once a month, with a mirror and good light.",
               "Face and neck, lips, cheeks, gums, tongue (top, sides, underneath), floor of the mouth, roof of the mouth, throat.",
               "You are looking for anything new: a patch, a sore, a lump, or a change in colour."]),

    # the numbers (each from seerStats.ts)
    "survival_by_stage": dict(
        pillar="stats", page="/learn/facts",
        tags={"stat"},
        kw=("survival", "88.7", "89%", "36%", "localized"),
        facts=["Five-year relative survival is about 89% when found while still localized,",
               "about 70% once it reaches nearby lymph nodes, and about 36% once it has spread to distant sites (SEER).",
               "Never call these Stage I or Stage IV: they are SEER summary stages."]),
    "found_late": dict(
        pillar="stats", page="/learn/facts",
        tags={"stat"},
        kw=("26%", "1 in 4", "caught early", "found early", "late"),
        facts=["Only about 26% of oral cancers are found while still localized (SEER).",
               "Most, about 55%, have already reached nearby lymph nodes by the time they are diagnosed."]),
    "yearly_numbers": dict(
        pillar="stats", page="/learn/facts",
        tags={"stat"},
        kw=("60,480", "13,150", "diagnosed this year", "deaths"),
        facts=["An estimated 60,480 Americans will be diagnosed with oral cavity or pharynx cancer in 2026,",
               "and about 13,150 will die of it (SEER 2026 estimates)."]),
    "screener_limits": dict(
        pillar="screener_cta", page="/methods",
        tags={"care", "myth"},
        kw=("screener", "risk score", "low result"),
        facts=["The OralCheck screener is free, private, takes a couple of minutes and needs no account.",
               "It reads back the exposures you report. It never sees your mouth and cannot tell you whether you have cancer.",
               "A low result is not a clean bill of health: a symptom still means see a dentist."]),
}

# ── shapes ────────────────────────────────────────────────────────────────────
# The structure of a post, independent of its subject. `needs` is the topic tag
# a shape requires (None means any topic works). `templates` are the posts2 or
# reel2 visuals the content step should build it from.

SHAPES: dict[str, dict[str, dict]] = {
    "carousel": {
        "quiz": dict(needs=None, templates=["quiz", "answer", "list", "cta"],
                     desc="Opens on a multiple-choice question about the topic, answers it on slide 2, then explains why."),
        "myth_fact": dict(needs="myth", templates=["cover", "split", "poster", "cta"],
                          desc="States a belief people genuinely hold, then takes it apart one slide at a time."),
        "guide": dict(needs="steps", templates=["cover", "mouthmap", "step", "cta"],
                      desc="A short illustrated how-to: one action per slide, drawn on the mouth diagram."),
        "compare": dict(needs="pair", templates=["cover", "compare", "list", "cta"],
                        desc="Two things that get confused, side by side, ending on how to tell them apart."),
        "notes": dict(needs="list", templates=["notes", "list", "cta"],
                      desc="Written like a phone note or checklist someone saved for themselves."),
        "timeline": dict(needs="timeline", templates=["cover", "calendar", "list", "cta"],
                         desc=("The two-week rule laid out on a calendar: what normally clears inside the window "
                               "and what still being there on day 15 means. Never imply symptoms arrive in a set order.")),
        "by_the_numbers": dict(needs="stat", templates=["bignum", "bignum", "split", "cta"],
                               desc="One figure per slide, each with one line of meaning."),
        "where_to_look": dict(needs="site", templates=["cover", "mouthmap", "step", "cta"],
                              desc="A tour of one place in the mouth: where it is, what normal looks like, what is not."),
    },
    "reel": {
        "quiz": dict(needs=None, templates=["quiz", "text", "cta"],
                     desc="Asks the viewer a question with a countdown, then reveals and explains the answer."),
        "myth": dict(needs="myth", templates=["myth", "text", "icons", "cta"],
                     desc="Names a belief, strikes it out, and replaces it with what is true."),
        "explainer": dict(needs="site", templates=["mouthmap", "text", "cta"],
                          desc="Animated walk around the mouth diagram, lighting each place as it is named."),
        "two_weeks": dict(needs="timeline", templates=["calendar", "text", "cta"],
                          desc=("A calendar fills day by day to the two-week mark while the voice explains what should have "
                               "cleared by then. Never imply symptoms arrive in a set order.")),
        "show_me": dict(needs="photo", templates=["photo", "text", "cta"],
                        desc="Shows a real clinical photo and walks through what the eye should notice."),
        "list": dict(needs="list", templates=["icons", "text", "cta"],
                     desc="A short spoken list, each item landing with its own icon."),
        "one_number": dict(needs="stat", templates=["stat", "bars", "cta"],
                           desc="Builds to a single figure, then shows what it means with bars."),
    },
    "image": {
        "poster": dict(needs=None, templates=["poster"],
                       desc="One bold sentence, big enough to read from across a room."),
        "big_number": dict(needs="stat", templates=["bignum"],
                           desc="One figure, huge, with a single line explaining it."),
        "textpost": dict(needs=None, templates=["textpost"],
                         desc="Looks like a short text post: plain, conversational, a thought worth sharing."),
        "notes": dict(needs="list", templates=["notes"],
                      desc="A phone-note style checklist someone would screenshot."),
        "this_or_that": dict(needs="pair", templates=["split"],
                             desc="Two halves, two things, one difference that matters."),
        "photo": dict(needs="photo", templates=["photo"],
                      desc="A real clinical photo with two or three short highlighted lines over it."),
        "calendar": dict(needs="timeline", templates=["calendar"],
                         desc="The fourteen-day calendar with day 15 flagged."),
        "diagram": dict(needs="site", templates=["mouthmap"],
                        desc="The mouth diagram with one place highlighted and labelled."),
    },
}

# ── hooks ─────────────────────────────────────────────────────────────────────
# How the first line opens. Assigned, so two posts in a batch never open alike.

HOOKS: dict[str, str] = {
    "question": "Opens with a direct question to the viewer that they can answer for themselves. Not 'Did you know'.",
    "scenario": "Opens on a concrete moment in second person: something the viewer notices, feels or does.",
    "number": "Opens with the specific figure, before any context.",
    "instruction": "Opens with a short physical instruction the viewer can do right now.",
    "contrast": "Opens by setting two things against each other.",
    "correction": "Opens by stating a belief plainly, then correcting it. Never attributes the belief to 'most people'.",
    "count": "Opens by promising a small specific number of things.",
    "plain": "Opens with one calm, plain sentence of fact, no setup.",
}

# Some openings only work on some topics. A number-led hook on a topic with no
# figure invites an invented one; a correction needs a belief worth correcting.
HOOK_NEEDS = {"number": {"stat"}, "correction": {"myth"}, "count": {"list", "pair"}}


def _hook_fits(hook: str, tags: set[str]) -> bool:
    need = HOOK_NEEDS.get(hook)
    return need is None or bool(need & tags)


# Phrases the old generator leaned on until they meant nothing. A title or hook
# containing one is regenerated rather than shipped.
BANNED = [
    r"\bmost (people|americans|adults|of us)\b",
    r"\bnobody (tells|talks|mentions)\b",
    r"\bno one (tells|talks|mentions)\b",
    r"\bdid you know\b",
    r"\bwhat you need to know\b",
    r"\bhere'?s (why|what|the)\b",
    r"\bhere is (why|what|how)\b",
    r"\bthe truth about\b",
    r"\byou won'?t believe\b",
    r"\bsilent killer\b",
    r"\bactually\b",
    r"\bmore than you (think|realize|realized)\b",
    r"\bnever (heard|hear) (of|about)\b",
    r"\bhave no idea\b",
    r"\bthat (number|is not true|isn'?t true)\b",
]
_BANNED_RE = re.compile("|".join(BANNED), re.IGNORECASE)


def banned_phrase(text: str) -> str | None:
    """The first overused phrase in `text`, or None."""
    m = _BANNED_RE.search(text or "")
    return m.group(0) if m else None


def two_sentence_title(title: str) -> bool:
    """The "Statement. Statement." title shape that every old idea used."""
    parts = [p for p in re.split(r"(?<=[.!?])\s+", (title or "").strip()) if p]
    return len(parts) >= 2


# ── assignment ────────────────────────────────────────────────────────────────

def _ts(value) -> float:
    try:
        ts = datetime.fromisoformat(value)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.timestamp()
    except (TypeError, ValueError):
        return 0.0


def infer_topic(idea: dict) -> str | None:
    """Best-guess topic for a ledger idea written before topics existed."""
    text = f"{idea.get('title', '')} {idea.get('brief', '')}".lower()
    best, hits = None, 0
    for key, t in TOPICS.items():
        n = sum(1 for k in t["kw"] if re.search(rf"(?<![\w]){re.escape(k)}(?![\w])", text))
        if n > hits:
            best, hits = key, n
    return best


def _last_seen(ledger: dict, field: str) -> dict[str, float]:
    """For each topic or shape value, how recently it was used.

    A post that was actually made counts at full weight. One that was only
    suggested counts too, but as if it were three weeks older, so a topic
    offered last week and passed over can come back sooner than one that ran.
    """
    seen: dict[str, float] = {}
    for i in ledger.get("ideas", []):
        val = i.get(field) or (infer_topic(i) if field == "topic" else None)
        if not val:
            continue
        if i.get("used_at"):
            t = _ts(i["used_at"])
        else:
            t = _ts(i.get("suggested_at")) - 21 * 86400
        seen[val] = max(seen.get(val, 0.0), t)
    return seen


def plan_slots(ledger: dict, media_list: list[str], *, seed: int | None = None,
               light_every: int = 4) -> list[dict]:
    """Assign topic, shape, hook and tone to each requested format slot.

    Least recently used wins for topics and shapes; ties break randomly so two
    runs on the same ledger still differ. Within one batch no topic repeats, no
    shape repeats within a format, and hook styles are dealt like cards.
    """
    rng = random.Random(seed)
    topic_seen = _last_seen(ledger, "topic")
    shape_seen = _last_seen(ledger, "shape")

    used_topics: set[str] = set()
    used_shapes: dict[str, set[str]] = {}
    hooks = list(HOOKS)
    rng.shuffle(hooks)
    used_hooks: set[str] = set()

    slots = []
    for n, media in enumerate(media_list):
        shapes = SHAPES[media]
        order = sorted(shapes, key=lambda s: (shape_seen.get(f"{media}:{s}", 0.0), rng.random()))
        picked = None
        for shape in order:
            if shape in used_shapes.get(media, set()):
                continue
            need = shapes[shape]["needs"]
            pool = [k for k, t in TOPICS.items()
                    if k not in used_topics and (need is None or need in t["tags"])]
            if not pool:
                continue
            topic = min(pool, key=lambda k: (topic_seen.get(k, 0.0), rng.random()))
            picked = (shape, topic)
            break
        if not picked:
            continue
        shape, topic = picked
        used_topics.add(topic)
        used_shapes.setdefault(media, set()).add(shape)
        tags = TOPICS[topic]["tags"]
        fits = [h for h in hooks if _hook_fits(h, tags)]
        hook = next((h for h in fits if h not in used_hooks), None) or rng.choice(fits)
        used_hooks.add(hook)
        slots.append({
            "media_type": media,
            "topic": topic,
            "shape": shape,
            "hook_style": hook,
            "tone": "light" if light_every and n % light_every == light_every - 1 else "calm",
            "pillar": TOPICS[topic]["pillar"],
        })
    return slots


def slot_brief(n: int, slot: dict) -> str:
    """The prompt block describing one slot to the model."""
    t = TOPICS[slot["topic"]]
    shape = SHAPES[slot["media_type"]][slot["shape"]]
    tone = ("Warm and gently witty, still respectful. Never a joke at a patient's expense."
            if slot["tone"] == "light" else "Calm and direct.")
    facts = "\n".join(f"      - {f}" for f in t["facts"])
    return (
        f"  Slot {n}: a {slot['media_type']}\n"
        f"    topic: {slot['topic']}  (oralcheck.org{t['page']})\n"
        f"    facts you may use, and nothing beyond them:\n{facts}\n"
        f"    shape: {slot['shape']}: {shape['desc']}\n"
        f"    hook: {slot['hook_style']}: {HOOKS[slot['hook_style']]}\n"
        f"    tone: {tone}"
    )
