#!/usr/bin/env python3
"""
Unit tests for the content calendar and idea ledger (the non-API logic).

Run:  python3.11 test_content.py   ->  exit 0 all pass, 1 on failure.
"""

import sys
from pathlib import Path
from datetime import date

import content_calendar as C
import engine as E
import ideas as I
import reel2d as R2D
import topics as T

_fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        _fails.append(name)


# --- Calendar --------------------------------------------------------------
def test_calendar():
    # World Head & Neck Cancer Day is July 27
    evs = {e["slug"]: e for e in C.upcoming(within_days=30, today=date(2026, 7, 10))}
    check("whncd surfaces mid-July", evs.get("world-head-neck-cancer-day", {}).get("days_until") == 17)

    # April is Oral Cancer Awareness Month; on Apr 15 it is active now (0 days)
    apr = {e["slug"]: e for e in C.upcoming(within_days=30, today=date(2026, 4, 15))}
    check("awareness month active in April", apr.get("oral-cancer-awareness-month", {}).get("days_until") == 0)

    # Great American Smokeout = 3rd Thursday of November 2026 -> Nov 19
    gaso = C.next_occurrence(
        {"rule": {"type": "nth-weekday", "month": 11, "weekday": 3, "n": 3}}, date(2026, 11, 1))
    check("nth-weekday resolves (Nov 19 2026)", gaso == date(2026, 11, 19))

    # Nothing within 5 days of a quiet date
    quiet = C.upcoming(within_days=5, today=date(2026, 6, 10))
    check("quiet window empty", quiet == [])


# --- Ledger / ideas --------------------------------------------------------
def test_slugify():
    check("slugify basic", I.slugify("HPV Is the Leading Cause!") == "hpv-is-the-leading-cause")
    check("slugify collapses", I.slugify("A  --  B") == "a-b")


def test_ledger_flow():
    ledger = {"ideas": [], "last_batch": []}
    fresh = [
        {"title": "Stat one", "slug": "stat-one", "pillar": "stats",
         "media_type": "carousel", "brief": "b", "angle": "surprising-true", "calendar_ref": None},
        {"title": "Myth two", "slug": "myth-two", "pillar": "myth_busting",
         "media_type": "image", "brief": "b", "angle": "myth", "calendar_ref": None},
    ]
    ledger = I.record_suggested(ledger, fresh)
    check("record assigns batch", len(ledger["last_batch"]) == 2)
    check("all suggested", all(i["status"] == "suggested" for i in ledger["ideas"]))

    chosen = I.select(ledger, [1])
    check("select returns one", len(chosen) == 1 and chosen[0]["title"] == "Stat one")
    check("selected status set", ledger["ideas"][0]["status"] == "selected")

    # Used slug is now off-limits; avoid list includes it
    check("used slug tracked", "stat-one" in I._used_slugs(ledger))
    check("avoid includes used", "Stat one" in I._avoid_titles(ledger))

    I.mark_queued(ledger, ledger["ideas"][0]["id"], "manifest_123")
    check("mark_queued sets status", ledger["ideas"][0]["status"] == "queued")
    check("mark_queued records manifest", ledger["ideas"][0]["manifest_id"] == "manifest_123")

    # Out-of-range picks are ignored, not crashing
    check("out-of-range pick ignored", I.select(ledger, [99]) == [])


def test_stale_claims():
    """An idea claimed by a run that died must come back, not vanish.

    `select()` marks an idea "selected" before the post is generated, so two
    runs cannot claim the same one. A run that dies in between leaves that
    status set forever, and "selected" is in USED_STATUSES, so the topic is
    never suggested again either. That is how the 2026-08-31 run stranded an
    idea that no later run could reach.
    """
    ledger = {"ideas": [], "last_batch": []}
    fresh = [
        {"title": "Claimed and stranded", "slug": "claimed-stranded", "pillar": "stats",
         "media_type": "carousel", "brief": "b", "angle": "surprising-true", "calendar_ref": None},
        {"title": "Claimed and built", "slug": "claimed-built", "pillar": "stats",
         "media_type": "image", "brief": "b", "angle": "surprising-true", "calendar_ref": None},
    ]
    ledger = I.record_suggested(ledger, fresh)
    I.select(ledger, [1, 2])
    I.mark_queued(ledger, ledger["ideas"][1]["id"], "manifest_abc")

    freed = I.release_stale_selected(ledger)
    check("the stranded claim is released", freed == [ledger["ideas"][0]["id"]])
    check("released idea is suggestable again",
          ledger["ideas"][0]["status"] == "suggested")
    check("a built idea is left alone",
          ledger["ideas"][1]["status"] == "queued"
          and ledger["ideas"][1]["manifest_id"] == "manifest_abc")
    check("the released title is no longer blocked",
          "Claimed and stranded" not in I._avoid_titles(ledger)
          or "claimed-stranded" not in I._used_slugs(ledger))
    check("releasing twice is a no-op", I.release_stale_selected(ledger) == [])


def test_coerce():
    good = I._coerce({"title": "T", "pillar": "stats", "media_type": "carousel",
                      "brief": "b", "angle": "a"}, {"stats"})
    check("coerce keeps valid", good is not None and good["media_type"] == "carousel")
    bad_media = I._coerce({"title": "T", "media_type": "hologram", "pillar": "stats"}, {"stats"})
    check("coerce fixes bad media", bad_media["media_type"] == "carousel")
    reel_ok = I._coerce({"title": "T", "media_type": "reel", "pillar": "stats"}, {"stats"})
    check("coerce keeps reel", reel_ok["media_type"] == "reel")
    bad_pillar = I._coerce({"title": "T", "pillar": "nope"}, {"stats"})
    check("coerce fixes bad pillar", bad_pillar["pillar"] == "stats")
    check("coerce drops empty title", I._coerce({"title": ""}, {"stats"}) is None)


class _Block:
    """Stand-in for an SDK text block."""
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _Resp:
    def __init__(self, *texts):
        self.content = [_Block(t) for t in texts]


def test_json_extraction():
    """A malformed idea response must cost ideas, never the run.

    On 2026-08-24 this raised a JSONDecodeError from inside a per-format loop,
    so the carousel and reel batches that had already generated were discarded
    and the weekly run died.
    """
    good = _Resp('[{"title": "A", "media_type": "reel"}, {"title": "B"}]')
    check("parses a clean array", len(I._extract_json_array(good)) == 2)

    fenced = _Resp('```json\n[{"title": "A"}]\n```')
    check("strips code fences", len(I._extract_json_array(fenced)) == 1)

    prose = _Resp('Here are the ideas:\n[{"title": "A"}]\nHope that helps.')
    check("ignores surrounding prose", len(I._extract_json_array(prose)) == 1)

    # One element malformed: keep the rest rather than losing everything.
    partial = _Resp('[{"title": "A"}, {"title": "B", oops}, {"title": "C"}]')
    got = I._extract_json_array(partial)
    check("salvages around a bad element", [i["title"] for i in got] == ["A", "C"])

    # Truncated mid-object, which is what a max_tokens cutoff looks like.
    cut = _Resp('[{"title": "A"}, {"title": "B"}, {"title": "C", "brief": "unfinis')
    got = I._extract_json_array(cut)
    check("salvages a truncated response", [i["title"] for i in got] == ["A", "B"])

    # Braces inside strings must not confuse the brace walker.
    braces = _Resp('[{"title": "A {not a brace} B"}]')
    got = I._extract_json_array(braces)
    check("ignores braces inside strings", got and got[0]["title"] == "A {not a brace} B")

    check("no array returns empty", I._extract_json_array(_Resp("no json here")) == [])
    check("never raises on junk", I._extract_json_array(_Resp("[[[")) == [])


# --- Topic, shape and hook assignment --------------------------------------
def test_slots():
    ledger = {"ideas": []}
    media = ["carousel"] * 3 + ["reel"] * 3 + ["image"] * 3
    slots = T.plan_slots(ledger, media, seed=7)
    check("every slot filled", len(slots) == 9)
    check("no topic repeats in a batch", len({s["topic"] for s in slots}) == 9)
    check("no shape repeats within a format",
          all(len({s["shape"] for s in slots if s["media_type"] == m}) == 3 for m in set(media)))
    check("hooks mostly distinct", len({s["hook_style"] for s in slots}) >= 6)
    for s in slots:
        need = T.SHAPES[s["media_type"]][s["shape"]]["needs"]
        if need and need not in T.TOPICS[s["topic"]]["tags"]:
            check(f"shape {s['shape']} fits topic {s['topic']}", False)
        if s["hook_style"] == "number" and "stat" not in T.TOPICS[s["topic"]]["tags"]:
            check(f"number hook only on a stat topic ({s['topic']})", False)

    # A topic used yesterday goes to the back of the queue.
    first = T.plan_slots(ledger, ["image"], seed=1)[0]
    used = {"ideas": [{"title": "x", "topic": first["topic"], "shape": "poster",
                       "used_at": "2026-10-07T00:00:00+00:00"}]}
    again = T.plan_slots(used, ["image"] * 6, seed=1)
    check("recently used topic is not picked first", again[0]["topic"] != first["topic"])

    check("old ideas infer a topic", T.infer_topic({"title": "Lift your tongue: the floor of the mouth"}) == "floor_of_mouth")
    check("substring does not match a keyword", T.infer_topic({"title": "an image post"}) is None)
    for key, t in T.TOPICS.items():
        if t.get("photo") and t["photo"] not in E.PHOTOS:
            check(f"{key} uses a cleared photo", False)


def test_voice_checks():
    check("bans 'most people'", T.banned_phrase("What most people miss about HPV") == "most people")
    check("bans 'did you know'", T.banned_phrase("Did you know this?") is not None)
    check("allows a plain line", T.banned_phrase("Lift your tongue to the roof of your mouth") is None)
    check("flags X. Y. titles", T.two_sentence_title("Ten Questions. Two Minutes."))
    check("allows one-line titles", not T.two_sentence_title("Floor of the mouth self-check"))
    bad = {"title": "60,000 Cases. Here's What That Means.", "hook": "x", "brief": "y"}
    check("idea problems caught", len(I._problems(bad)) >= 2)


# --- Engine spec validation (no API) ----------------------------------------
def test_engine_validation():
    slides = E.validate_slides([
        {"template": "cover", "hook": "Lift your *tongue*", "kicker": "Self-check"},
        {"template": "hologram", "text": "x"},
        {"template": "icons", "title": "T", "items": [{"icon": "sun", "label": "a"},
                                                     {"icon": "nope", "label": "b"},
                                                     {"icon": "alcohol", "label": "c"},
                                                     {"icon": "tobacco", "label": "d"}]},
        {"template": "photo", "photo": "sore", "lines": ["a"]},
        {"template": "step", "n": 1, "area": "Floor", "text": "Look under", "zone": "nowhere"},
        {"template": "cta"},
        {"template": "poster", "text": "Two \u2014 weeks"},
    ], "carousel")
    kinds = [s["type"] for s in slides]
    check("unknown template dropped", "hologram" not in kinds)
    check("uncleared photo dropped", "photo" not in kinds)
    check("unknown icons filtered", all(i["icon"] != "nope" for s in slides if s["type"] == "icons" for i in s["items"]))
    check("cta moved to the end, once", kinds[-1] == "cta" and kinds.count("cta") == 1)
    check("step without a zone gets an icon", any(s["type"] == "step" and s.get("icon") for s in slides))
    check("em dashes stripped", all("\u2014" not in str(s) for s in slides))
    check("image keeps one slide", len(E.validate_slides([{"template": "poster", "text": "a"},
                                                          {"template": "poster", "text": "b"}], "image")) == 1)

    beats = E.validate_beats([
        {"say": "Quick test.", "visual": {"type": "quiz", "question": "Q", "options": ["a", "b"]}, "hold": 9},
        {"say": "Nope.", "visual": {"type": "stamp", "text": "NOPE"}},
        {"say": "Look here.", "visual": {"type": "photo", "photo": "lip"}},
        {"say": "Go.", "visual": {"type": "cta"}},
    ])
    check("hold clamped", beats[0]["hold"] <= 2.4)
    check("retired stamp visual becomes text", beats[1]["visual"]["type"] == "text")
    check("uncleared reel photo becomes text", beats[2]["visual"]["type"] == "text")
    check("reel ends on one cta", beats[-1]["visual"]["type"] == "cta"
          and sum(b["visual"]["type"] == "cta" for b in beats) == 1)


# --- illustrated reels (no API, no render) ----------------------------------
def test_reel2d():
    import json
    # Ian's review notes, 2026-10-21: what the voice names is what lights up.
    check("lips get the lips, not the teeth", R2D.match_focus("Check your lips for any change.", "teeth") == "lips")
    check("the inner cheek gets the cheek, not the floor",
          R2D.match_focus("Look for patches on the inner cheek.", "floor") == "cheek")
    check("'redness or a patch' stays on the topic", R2D.match_focus("Watch for redness or a patch.", "teeth", "gums") == "gums")
    check("tonsils are the tonsils", R2D.match_focus("The tonsils sit at the back.", "tongue") == "tonsil")
    check("the base of the tongue is not the tongue", R2D.match_focus("It starts at the base of the tongue.", "tongue") == "base")
    check("the soft palate is the throat", R2D.match_focus("Look at the soft palate.", "overview") == "throat")
    check("the roof of the mouth is the palate", R2D.match_focus("Check the roof of your mouth.", "overview") == "palate")
    # The 27 Oct rebuild said "run your tongue along your gumline" and lit the tongue.
    check("the gumline is the gums", R2D.match_focus("Run your tongue along your gumline and look for swelling.", "gums") == "gums")
    check("the neck is the lymph nodes", R2D.match_focus("Feel along your neck for a lump.", "overview") == "nodes")
    check("under the jaw is the neck", R2D.match_focus("Feel under your jaw for any lump.", "overview", "tongue") == "nodes")
    # signs are drawn only where the line puts them
    check("a white patch with no place goes to the tongue",
          R2D.lesion_for("A white patch that will not wipe away.", "overview") == ("tongue", "white"))
    check("'won't wipe away' is not thrush", R2D.lesion_kind("A white patch that won't wipe away.") == "white")
    check("'wipes away' is thrush", R2D.lesion_kind("Thrush usually wipes away.") == "thrush")
    check("a sign is never drawn somewhere else",
          R2D.lesion_for("Redness or a patch along the gumline.", "gums") == ("gums", None))
    check("a lip sore is drawn on the lip", R2D.lesion_for("A sore on the lip.", "lips") == ("lips", "lip"))
    check("every drawn sign has an anchor", all(l in R2D.LESIONS for d in R2D.LESION_AT.values() for l in d.values()))
    check("lesion shots drop the teal tint", R2D._shot("tongue", "white")["hi"] == [])
    # 6 Nov reel (26 Oct): "if a patch is still there after two weeks" lit and labelled the lips
    check("a line naming no place never shows a place the writer picked",
          R2D.match_focus("If a patch is still there after two weeks, get it checked.", "lips", None) == "overview")
    check("a topic with one place keeps it for unnamed lines", T.home_for("gums_mimic") == "gums" and T.home_for("painless") is None)
    # 27 Oct reel: "promised six, showed three"
    shown = [{"focus": "lips"}, {"focus": "cheek"}, {"focus": "tongue"}]
    check("a caption naming places no shot shows is caught",
          R2D.unshown_places("Your dentist checks your lips, gums, tongue and the back of your throat.", shown) == ["gums", "throat"])
    import oralcheck_agent as _A
    bad = {"type": "photocompare", "a_sign": "sore", "a_label": "Oral thrush: wipes away",
           "b_sign": "white_patch", "b_label": "Leukoplakia: stays put"}
    good = {"type": "photocompare", "a_sign": "white_patch", "a_label": "A white patch (leukoplakia)",
            "b_sign": "mixed_patch", "b_label": "A speckled red and white patch"}
    check("a photo pair captioned as something else is dropped (2 Dec carousel)",
          not any(s.get("type") == "photocompare" for s in _A.build_deck_from_content({"slides": [dict(bad)]}, None)["slides"]))
    check("a correctly labelled photo pair stays",
          any(s.get("type") == "photocompare" for s in _A.build_deck_from_content({"slides": [dict(good)]}, None)["slides"]))
    # 26 Oct, Ian's second pass
    check("a patch on the cheek is drawn on the cheek",
          R2D.lesion_for("A white or red patch on the inside of the cheek.", "cheek") == ("cheek", "whitecheek"))
    check("a patch of no stated colour is still drawn",
          R2D.lesion_for("The same painless patches appear on the sides of the tongue.", "tongue") == ("tongue", "white"))
    lists = [v for v in T.VISUAL.values() if v[0] == "list"]
    check("list posts carry their items and a closing line, no em dashes",
          lists and all(len(v[1]) >= 3 and v[2] and not any("\u2014" in x for x in v[1] + [v[2]]) for v in lists))
    check("HPV throat pictures use the side view, not the open mouth up close",
          all(T.VISUAL[k][1] == "oropharynx" for k in ("hpv_overtook_tobacco", "hpv_who", "hpv_is_common", "throat_hpv_site")))
    import reel2 as _R2
    check("the music sits well under the voice", _R2.MUSIC_UNDER_VOICE >= 24)
    check("the throat is shown by the tonsils", R2D.unshown_places("HPV throat cancer.", [{"focus": "tonsil"}]) == [])
    # sources and pictures
    check("every cited source is on the verified list", all(k in T.CITES for ks in T.TOPIC_CITES.values() for k in ks))
    check("statistics posts cite SEER", T.source_line("survival_by_stage") == "Source: NCI SEER")
    check("risk posts cite the paper", T.source_line("tobacco_plus_alcohol") == "Source: Hashibe et al., 2009")
    check("caption sources carry links", "pubmed.ncbi.nlm.nih.gov/19190158" in T.caption_sources("tobacco_plus_alcohol"))
    check("how-to topics cite nothing", T.source_line("monthly_self_exam") == "")
    check("every picture rule names a real topic", all(t in T.TOPICS for t in T.VISUAL))
    check("plate pictures use real foci and signs",
          all(v[1] in R2D.FOCI and (len(v) < 3 or v[2] in R2D.LESIONS) for v in T.VISUAL.values() if v[0] == "plate"))
    check("paired pictures use real signs",
          all(l in R2D.LESIONS and f in R2D.FOCI for v in T.VISUAL.values() if v[0] == "pair" for f, l, _, _ in v[1]))
    check("sign pictures are only the two attributed photos",
          all(v[1] in ("white_patch", "mixed_patch") for v in T.VISUAL.values() if v[0] == "sign"))
    check("no picture is a retired 3D still", all(v[0] != "3d" for v in T.VISUAL.values()))
    check("every topic focus is a real plate focus",
          all(f in R2D.FOCI for fs in T.TOPIC_FOCI.values() for f in fs))
    check("unknown topics still get foci", T.foci_for("no_such_topic")[0] == "overview")
    plan = R2D.validate({"shots": [{"say": "Look here.", "focus": "tongue", "label": {"k": "a", "t": "b", "d": "c"}},
                                   {"say": "Then here.", "focus": "spleen"},
                                   {"say": "", "focus": "floor"},
                                   {"say": "Go.", "focus": "cta"}]})
    kinds = [s["focus"] for s in plan["shots"]]
    check("unknown focus becomes overview", kinds[1] == "overview")
    check("empty lines dropped", len(plan["shots"]) == 3)
    check("ends on exactly one end card", kinds[-1] == "cta" and kinds.count("cta") == 1)
    check("overview shots carry no label", plan["shots"][1]["label"] is None)

    calls = []
    def ask(prompt):
        calls.append(prompt)
        return json.dumps({"shots": [{"say": "Most mouth cancers start somewhere you can see.", "focus": "overview"},
                                     {"say": "Check the sides of your tongue.", "focus": "teeth",
                                      "label": {"k": "Where", "t": "Teeth", "d": "x"}},
                                     {"say": "Look under your tongue as well.", "focus": "tonsils_nope"},
                                     {"say": "A red or white patch that lasts matters.", "focus": "teeth"}],
                           "caption": "Check your risk at oralcheck.org.", "hashtags": ["A", "b"]})
    spec = E.write_reel2d({"topic": "tongue_sides", "media_type": "reel", "shape": "close_look",
                           "hook_style": "plain", "brief": "x"}, ask)
    foci = [s["focus"] for s in spec["shots"]]
    check("a line naming the tongue lights the tongue", foci[1] == "tongue")
    check("a refocused shot drops its wrong label", spec["shots"][1]["label"] is None)
    check("'under your tongue' is the floor of the mouth", foci[2] == "floor")
    check("a line naming no place never lights the teeth", foci[3] in ("tongue", "overview"))
    check("only the topic's foci are offered", "Salivary" not in calls[0] and "Tongue" in calls[0])
    check("credit line in the caption", R2D.CREDIT in spec["caption"])
    check("hashtags lowercased", spec["hashtags"] == ["a", "b"])


# --- posting calendar ------------------------------------------------------
def test_post_calendar():
    import collections, tempfile, json
    from datetime import date as _d, datetime as _dt
    import post_calendar as PC
    slots = PC.plan_dates(_d(2026, 10, 26), 10)
    check("30 dates over ten weeks", len(slots) == 30)
    check("10 reels, 10 carousels, 10 images",
          collections.Counter(s["media_type"] for s in slots) == {"reel": 10, "carousel": 10, "image": 10})
    check("reels only on Instagram", all(s["network"] == "instagram" for s in slots if s["media_type"] == "reel"))
    check("one LinkedIn post a week", sum(s["network"] == "linkedin" for s in slots) == 10)
    check("every post at 10am Central across the DST change",
          all(_dt.fromisoformat(s["when"]).astimezone(PC.CT).hour == 10 for s in slots))
    check("only on Mondays, Tuesdays and Thursdays",
          all(_d.fromisoformat(s["date"]).weekday() in (0, 1, 3) for s in slots))

    # decisions from the review page land on the calendar, never on a scheduled post
    old_file, old_dir = PC.CAL_FILE, PC.CAL_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PC.CAL_DIR = PC.Path(tmp); PC.CAL_FILE = PC.CAL_DIR / "calendar.json"
        PC.save({"entries": [{"id": "a", "status": "built"}, {"id": "b", "status": "built"},
                             {"id": "c", "status": "scheduled"}]})
        counts = PC.apply_decisions([{"id": "a", "decision": "approve"}, {"id": "b", "decision": "redo", "note": "shorter"},
                                     {"id": "c", "decision": "cut"}, {"id": "zz", "decision": "approve"}])
        cal = PC.load()
        st = {e["id"]: e["status"] for e in cal["entries"]}
        check("approve and redo applied", st["a"] == "approved" and st["b"] == "redo")
        check("a scheduled post is not touched", st["c"] == "scheduled")
        check("redo note kept", cal["entries"][1]["review_note"] == "shorter")
        check("unknown ids ignored", counts == {"approved": 1, "redo": 1})
        # a rebuilt post is a new version; a decision about the old one does not carry over
        PC.save({"entries": [{"id": "a", "status": "built", "version": 2}]})
        PC.apply_decisions([{"id": "a", "decision": "approve", "v": 1}])
        check("stale decision ignored", PC.load()["entries"][0]["status"] == "built")
        PC.apply_decisions([{"id": "a", "decision": "approve", "v": 2}])
        check("current decision applied", PC.load()["entries"][0]["status"] == "approved")
    PC.CAL_FILE, PC.CAL_DIR = old_file, old_dir

    import oralcheck_agent as A
    check("a site screenshot needs no photo credit", A._credit_line("oralcheck.org") == "")


def test_meta_publish():
    """Direct Instagram publishing: what is due, what is too late, and the switch."""
    import os
    from datetime import datetime, timedelta, timezone
    import post_calendar as PC, meta_ig as M
    now = datetime(2026, 10, 27, 15, 10, tzinfo=timezone.utc)
    def e(i, net, status, mins, **kw):
        return {"id": i, "network": net, "status": status, "media_type": "image",
                "when": (now + timedelta(minutes=mins)).isoformat(), **kw}
    cal = {"entries": [e("due", "instagram", "approved", -10), e("future", "instagram", "approved", 30),
                       e("li", "linkedin", "approved", -10), e("built", "instagram", "built", -10),
                       e("late", "instagram", "approved", -60 * 7), e("tried", "instagram", "approved", -5, publish_attempts=3)]}
    due, late = PC.due_for_instagram(cal, now)
    check("only the due, approved Instagram post is sent", [x["id"] for x in due] == ["due"])
    check("a post over six hours late is held back", [x["id"] for x in late] == ["late"])
    old = os.environ.pop("IG_DIRECT", None)
    check("Publora stays in charge until IG_DIRECT=1", not PC.ig_direct() and PC.publish() == [])
    if old is not None:
        os.environ["IG_DIRECT"] = old
    cap = M.full_caption({"caption": "Hi", "hashtags": ["a", "b"]})
    check("caption ends with the hashtags", cap == "Hi\n\n#a #b")
    try:
        M.full_caption({"caption": "x" * 2300}); ok = False
    except M.MetaError:
        ok = True
    check("a caption over 2,200 characters is refused, not cut", ok)
    try:
        M.post_carousel([Path("a.jpg")], "x"); ok = False
    except M.MetaError:
        ok = True
    check("a one-picture carousel is refused before any upload", ok)


def main():
    print("Calendar:");      test_calendar()
    print("Instagram direct:"); test_meta_publish()
    print("Post calendar:"); test_post_calendar()
    print("Illustrated reels:"); test_reel2d()
    print("Slots:");         test_slots()
    print("Voice checks:");  test_voice_checks()
    print("Engine specs:");  test_engine_validation()
    print("Slugify:");       test_slugify()
    print("Ledger flow:");   test_ledger_flow()
    print("Stale claims:");  test_stale_claims()
    print("Coerce:");        test_coerce()
    print("JSON extraction:"); test_json_extraction()
    if _fails:
        print(f"\n  {len(_fails)} FAILURE(S): {', '.join(_fails)}")
        return 1
    print("\n  All content-logic checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
