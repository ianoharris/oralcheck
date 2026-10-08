#!/usr/bin/env python3
"""
Unit tests for the content calendar and idea ledger (the non-API logic).

Run:  python3.11 test_content.py   ->  exit 0 all pass, 1 on failure.
"""

import sys
from datetime import date

import content_calendar as C
import engine as E
import ideas as I
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


def main():
    print("Calendar:");      test_calendar()
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
