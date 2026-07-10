"""
Content calendar for OralCheck: awareness days and tasteful holidays that warrant
branded posts. Pure data/logic, no dependency on the agent, so it can be imported
anywhere and unit-tested in isolation.
"""

import json
from datetime import date, timedelta
from pathlib import Path

CALENDAR_FILE = Path(__file__).parent / "content_calendar.json"


def load_events() -> list[dict]:
    if not CALENDAR_FILE.exists():
        return []
    with open(CALENDAR_FILE) as f:
        return json.load(f)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The date of the nth <weekday> in a month (weekday: Mon=0..Sun=6)."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def next_occurrence(event: dict, today: date) -> date:
    """The next date this event is 'anchored' to, on or after today.

    Month-long events anchor to the first of the month; if today is already
    within that month, they anchor to today (they are active now).
    """
    rule = event["rule"]
    rt = rule["type"]

    def for_year(y: int) -> date:
        if rt == "fixed":
            return date(y, rule["month"], rule["day"])
        if rt == "month":
            return date(y, rule["month"], 1)
        if rt == "nth-weekday":
            return _nth_weekday(y, rule["month"], rule["weekday"], rule["n"])
        raise ValueError(f"unknown rule type: {rt}")

    if rt == "month" and today.month == rule["month"]:
        return today  # active now

    occ = for_year(today.year)
    if occ < today:
        occ = for_year(today.year + 1)
    return occ


def upcoming(within_days: int = 30, today: date | None = None) -> list[dict]:
    """Events whose anchor falls within `within_days` of today, soonest first.

    Each returned dict is the event plus 'date' (ISO) and 'days_until'.
    """
    today = today or date.today()
    out = []
    for ev in load_events():
        occ = next_occurrence(ev, today)
        days_until = (occ - today).days
        if 0 <= days_until <= within_days:
            out.append({**ev, "date": occ.isoformat(), "days_until": days_until})
    out.sort(key=lambda e: e["days_until"])
    return out
