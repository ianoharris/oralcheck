#!/usr/bin/env python3
"""
OralCheck Studio: the posting calendar as an app, on the PC hub.

Runs on ianspc as a user service (studio/install.sh), loopback only, opened over
the tailnet with `tailscale serve`. Ian's Mac and phone reach it; nothing else does.

How it stays current
  * ~/oralcheck-studio/repo is a clone of the repo. It pulls every two minutes, so
    when the daily GitHub job posts something, it leaves the calendar here by itself.
  * Every button writes to oralcheck-agent/calendar/calendar.json and pushes, the
    same file the posting jobs and the Mac read. Each write starts from a fresh
    fetch, so the Studio never overwrites the bot or a Claude session.
  * Media is not in git (the repo is public). The Mac copies each built post into
    this clone's calendar/<id>/ folders (post_calendar.py studio-sync), and Approve
    uploads it to the release CI posts from, as `post_calendar.py upload` does.
  * Photos Ian drops in stay in ~/oralcheck-studio/photos/<entry id>/; only their
    count is recorded in the calendar. The Mac pulls them with studio-sync.

Ian's choices (23 Nov 2026): approve means it posts; every redo waits for a Claude
session (status "redo" with his note in review_note); posted and cut posts leave the
calendar for their own tabs; the idea suggester runs the Claude Code CLI on this PC,
only when he presses the button, never the API; a post can ask him for photos
(drag, drop or paste) and yes/no decisions.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

HOME = Path(os.environ.get("STUDIO_HOME", Path.home() / "oralcheck-studio"))
REPO = HOME / "repo"
AGENT = REPO / "oralcheck-agent"
CAL_DIR = AGENT / "calendar"
CAL = CAL_DIR / "calendar.json"
DATA = HOME / "data"
PHOTOS = HOME / "photos"
THUMBS = DATA / "thumbs"
IDEAS = DATA / "ideas.json"
INSIGHTS = DATA / "insights.json"
KEYS = HOME / "keys"
HERE = Path(__file__).parent
CT = ZoneInfo("America/Chicago")
GH_REPO = "ianoharris/oralcheck"
CLAUDE = os.environ.get("STUDIO_CLAUDE", str(Path.home() / ".local/bin/claude"))
PULL_EVERY = 120
for d in (DATA, PHOTOS, THUMBS, KEYS):
    d.mkdir(parents=True, exist_ok=True)

LOCK = threading.RLock()          # one git operation at a time
STATE = {"last_pull": None, "pull_error": None, "ideas_run": None, "insights_run": None}
app = FastAPI(title="OralCheck Studio")


# ---- git ----------------------------------------------------------------------------------
def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[-400:]}")
    return r


def pull() -> None:
    with LOCK:
        before = git("rev-parse", "HEAD", check=False).stdout.strip()
        r = git("pull", "--rebase", "--autostash", "-q", "origin", "master", check=False)
        STATE["last_pull"] = datetime.now(timezone.utc).isoformat()
        STATE["pull_error"] = None if r.returncode == 0 else r.stderr.strip()[-300:]
        after = git("rev-parse", "HEAD", check=False).stdout.strip()
        if before and after != before and git("diff", "--name-only", before, after, "--", "oralcheck-agent/studio/*.py",
                                              check=False).stdout.strip():
            # the app's own code changed: exit, and systemd starts the new version
            threading.Timer(1.0, lambda: os._exit(0)).start()


def load() -> dict:
    return json.loads(CAL.read_text())


def mutate(message: str, fn):
    """Apply fn(calendar) on top of the latest origin/master, commit and push.
    Retries if someone else (the posting bot, a Claude session) pushed first."""
    with LOCK:
        last = ""
        for _ in range(4):
            git("fetch", "-q", "origin", "master")
            git("reset", "-q", "--hard", "origin/master")      # media folders are untracked and survive this
            cal = load()
            result = fn(cal)
            CAL.write_text(json.dumps(cal, indent=2))
            if not git("status", "--porcelain", "--", str(CAL), check=False).stdout.strip():
                return result
            git("commit", "-q", "-m", f"Studio: {message}", "--", str(CAL))
            p = git("push", "-q", "origin", "HEAD:master", check=False)
            if p.returncode == 0:
                STATE["last_pull"] = datetime.now(timezone.utc).isoformat()
                return result
            last = p.stderr.strip()[-300:]
            time.sleep(2)
        git("reset", "-q", "--hard", "origin/master", check=False)
        raise HTTPException(503, f"Could not save to GitHub: {last}")


def entry(cal: dict, eid: str) -> dict:
    for e in cal["entries"]:
        if e["id"] == eid:
            return e
    raise HTTPException(404, f"No post {eid}")


def _puller() -> None:
    while True:
        try:
            pull()
        except Exception as exc:  # noqa: BLE001
            STATE["pull_error"] = str(exc)[:300]
        time.sleep(PULL_EVERY)


# ---- derived state ----------------------------------------------------------------------
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def lane(e: dict) -> str:
    """Which tab a post belongs on."""
    s = e["status"]
    when = datetime.fromisoformat(e["when"])
    if s == "posted" or (s == "scheduled" and when < now_utc()):
        return "posted"
    if s == "cut":
        return "cut"
    if s == "redo":
        return "redo"
    return "upcoming"


def needs(e: dict) -> list[dict]:
    """What this post is waiting on Ian for."""
    out = []
    if lane(e) != "upcoming":
        return out
    for a in e.get("asks", []):
        if a.get("kind") == "photo" and not a.get("files"):
            out.append({"kind": "photo", "id": a["id"], "q": a["q"]})
        elif a.get("kind") == "yesno" and a.get("answer") is None:
            out.append({"kind": "yesno", "id": a["id"], "q": a["q"]})
    if e["status"] == "built":
        out.append({"kind": "approve", "q": "Watch it and approve, redo or cut"})
    return out


def media_files(e: dict) -> list[str]:
    folder = CAL_DIR / (e.get("folder") or e["id"])
    if not folder.is_dir():
        return []
    names = e.get("files") or []
    if not names:
        mf = folder / "manifest.json"
        if mf.exists():
            names = json.loads(mf.read_text()).get("files", [])
    return [n for n in names if (folder / n).exists() and n != "preview.jpg"]


def insights_by_entry(cal: dict) -> dict:
    if not INSIGHTS.exists():
        return {}
    data = json.loads(INSIGHTS.read_text())
    by_id = {m["id"]: m for m in data.get("media", [])}
    out = {}
    for e in cal["entries"]:
        m = by_id.get(str(e.get("ig_media_id") or ""))
        if not m:
            continue
        # ig_insights.metric gives a number, None, or {"error": ...} when Meta does not offer it
        ins = {k: (None if isinstance(v, dict) else v) for k, v in (m.get("insights") or {}).items()}
        out[e["id"]] = {"permalink": m.get("permalink"), **ins}
    return out


def public(e: dict, ins: dict) -> dict:
    when = datetime.fromisoformat(e["when"]).astimezone(CT)
    return {
        "id": e["id"], "date": e["date"], "when_ct": when.strftime("%a %-d %b, %-I:%M %p"), "network": e["network"],
        "media_type": e["media_type"], "status": e["status"], "lane": lane(e), "title": e["idea"].get("title", ""),
        "hook": e.get("hook") or e["idea"].get("hook", ""), "caption": e.get("caption") or "",
        "series": e["idea"].get("series"), "shape": e["idea"].get("shape"), "version": e.get("version"),
        "media": media_files(e), "needs": needs(e), "asks": e.get("asks", []),
        "review_note": e.get("review_note"), "redo_at": e.get("redo_at"), "cut_reason": e.get("cut_reason"),
        "notes": (e.get("notes") or [])[-3:], "uploaded": e.get("uploaded", False),
        "insights": ins.get(e["id"]), "approved_at": e.get("approved_at"), "posted_at": e.get("posted_at"),
    }


# ---- pages --------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return (HERE / "index.html").read_text()


@app.get("/api/state")
def state():
    cal = load()
    ins = insights_by_entry(cal)
    head = git("log", "-1", "--format=%h %s", check=False).stdout.strip()
    return {"entries": [public(e, ins) for e in sorted(cal["entries"], key=lambda e: e["when"])],
            "ideas": _ideas()["ideas"], "state": STATE, "head": head,
            "insights_at": json.loads(INSIGHTS.read_text()).get("_fetched_at") if INSIGHTS.exists() else None}


@app.post("/api/sync")
def sync():
    pull()
    return {"ok": STATE["pull_error"] is None, "error": STATE["pull_error"]}


@app.get("/media/{eid}/{name}")
def media(eid: str, name: str):
    e = entry(load(), eid)
    if name not in media_files(e):
        raise HTTPException(404)
    return FileResponse(CAL_DIR / (e.get("folder") or e["id"]) / name)


@app.get("/thumb/{eid}.jpg")
def thumb(eid: str):
    e = entry(load(), eid)
    files = media_files(e)
    if not files:
        raise HTTPException(404)
    src = CAL_DIR / (e.get("folder") or e["id"]) / files[0]
    out = THUMBS / f"{eid}_v{e.get('version') or 0}_{int(src.stat().st_mtime)}.jpg"
    if not out.exists():
        if src.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=540:-1", str(out)]
        else:
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", "0.6", "-i", str(src), "-frames:v", "1", "-vf", "scale=540:-1", str(out)]
        subprocess.run(cmd, check=False)
    if not out.exists():
        raise HTTPException(404)
    return FileResponse(out)


@app.get("/photo/{eid}/{name}")
def photo(eid: str, name: str):
    p = PHOTOS / eid / name
    if not re.fullmatch(r"[\w.-]+", name) or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


# ---- decisions ------------------------------------------------------------------------------
def _stamp() -> str:
    return datetime.now(CT).strftime("%-d %b %Y")


@app.post("/api/entry/{eid}/approve")
def approve(eid: str):
    def fn(cal):
        e = entry(cal, eid)
        if e["status"] != "built":
            raise HTTPException(409, f"Only a built post can be approved (this one is {e['status']}).")
        e.update(status="approved", approved_at=now_utc().isoformat())
        e.setdefault("notes", []).append(f"{_stamp()}: approved in the Studio.")
    mutate(f"approve {eid}", fn)
    return {"ok": True, "upload": _upload(eid)}


def _upload(eid: str) -> str:
    """Put the approved media on the release the posting job reads from."""
    e = entry(load(), eid)
    if not media_files(e):
        return "Approved. Its media has not reached the PC yet, so it uploads at the next Mac sync."
    with LOCK:
        git("fetch", "-q", "origin", "master"); git("reset", "-q", "--hard", "origin/master")
        r = subprocess.run([sys.executable, "post_calendar.py", "upload"], cwd=AGENT, capture_output=True, text=True)
        if r.returncode != 0:
            git("reset", "-q", "--hard", "origin/master", check=False)
            return "Approved, but the upload failed: " + r.stderr.strip()[-300:]
        if git("status", "--porcelain", "--", str(CAL), check=False).stdout.strip():
            git("commit", "-q", "-m", f"Studio: upload {eid}", "--", str(CAL))
            if git("push", "-q", "origin", "HEAD:master", check=False).returncode != 0:
                git("reset", "-q", "--hard", "origin/master", check=False)
                return "Uploaded, but saving the upload flag failed; the next upload run will fix it."
    return "Approved and uploaded. It posts on its date."


@app.post("/api/entry/{eid}/undo")
def undo(eid: str):
    def fn(cal):
        e = entry(cal, eid)
        if e["status"] != "approved":
            raise HTTPException(409, "Only an approved post that has not been scheduled can be taken back.")
        e["status"] = "built"
        e.setdefault("notes", []).append(f"{_stamp()}: approval taken back in the Studio.")
    mutate(f"un-approve {eid}", fn)
    return {"ok": True}


@app.post("/api/entry/{eid}/redo")
async def redo(eid: str, request: Request):
    body = await request.json()
    note = (body.get("note") or "").strip()
    if not note:
        raise HTTPException(400, "Say what should change.")
    def fn(cal):
        e = entry(cal, eid)
        if e["status"] in ("posted", "scheduled"):
            raise HTTPException(409, "It is already scheduled or posted.")
        e.update(status="redo", review_note=note, redo_from=e["status"], redo_at=now_utc().isoformat())
        e.setdefault("notes", []).append(f"{_stamp()}: sent back in the Studio: {note}")
    mutate(f"redo {eid}", fn)
    return {"ok": True}


@app.post("/api/entry/{eid}/cut")
async def cut(eid: str, request: Request):
    body = await request.json()
    reason = (body.get("reason") or "").strip() or "Cut in the Studio."
    def fn(cal):
        e = entry(cal, eid)
        if e["status"] in ("posted",):
            raise HTTPException(409, "It has already posted.")
        e.update(status="cut", cut_reason=reason, cut_from=e["status"], cut_at=now_utc().isoformat())
        e.setdefault("notes", []).append(f"{_stamp()}: cut in the Studio: {reason}")
    mutate(f"cut {eid}", fn)
    return {"ok": True}


@app.post("/api/entry/{eid}/restore")
def restore(eid: str):
    def fn(cal):
        e = entry(cal, eid)
        if e["status"] != "cut":
            raise HTTPException(409, "Only a cut post can be restored.")
        back = e.get("cut_from") or "planned"
        e["status"] = "built" if back in ("approved", "scheduled") else back
        e.setdefault("notes", []).append(f"{_stamp()}: restored in the Studio.")
    mutate(f"restore {eid}", fn)
    return {"ok": True}


@app.post("/api/entry/{eid}/ask/{aid}")
async def answer(eid: str, aid: str, request: Request):
    body = await request.json()
    ans = body.get("answer")
    if ans not in ("yes", "no"):
        raise HTTPException(400, "Answer yes or no.")
    def fn(cal):
        e = entry(cal, eid)
        for a in e.get("asks", []):
            if a["id"] == aid:
                a.update(answer=ans, answered_at=now_utc().isoformat(), handled=False)
                return
        raise HTTPException(404, "No such question.")
    mutate(f"answer on {eid}", fn)
    return {"ok": True}


ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".gif"}


@app.post("/api/entry/{eid}/photo/{aid}")
async def add_photos(eid: str, aid: str, files: list[UploadFile]):
    entry(load(), eid)
    folder = PHOTOS / eid
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower() or {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(f.content_type or "", "")
        if ext not in ALLOWED:
            raise HTTPException(400, f"{f.filename}: only photos (jpg, png, webp, heic).")
        name = f"{aid}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}{ext}"   # no original names: they can carry personal detail
        data = await f.read()
        if len(data) > 40 * 1024 * 1024:
            raise HTTPException(400, f"{f.filename}: over 40 MB.")
        (folder / name).write_bytes(data)
        saved.append(name)
    def fn(cal):
        e = entry(cal, eid)
        for a in e.get("asks", []):
            if a["id"] == aid:
                a["files"] = sorted(set(a.get("files", [])) | set(saved))
                a["handled"] = False
                return
        raise HTTPException(404, "No such photo request.")
    mutate(f"{len(saved)} photo(s) for {eid}", fn)
    return {"ok": True, "saved": saved}


@app.delete("/api/entry/{eid}/photo/{aid}/{name}")
def remove_photo(eid: str, aid: str, name: str):
    if not re.fullmatch(r"[\w.-]+", name):
        raise HTTPException(400)
    p = PHOTOS / eid / name
    if p.exists():
        (PHOTOS / eid / "removed").mkdir(exist_ok=True)
        p.rename(PHOTOS / eid / "removed" / name)        # kept, out of the way
    def fn(cal):
        for a in entry(cal, eid).get("asks", []):
            if a["id"] == aid:
                a["files"] = [x for x in a.get("files", []) if x != name]
    mutate(f"photo removed from {eid}", fn)
    return {"ok": True}


# ---- ideas (Claude Code CLI on this PC, only when Ian presses the button) ------------------
def _ideas() -> dict:
    return json.loads(IDEAS.read_text()) if IDEAS.exists() else {"ideas": [], "runs": []}


def _save_ideas(d: dict) -> None:
    IDEAS.write_text(json.dumps(d, indent=1))


def _numbers_digest(cal: dict) -> Path:
    """Per-post numbers joined to what each post was, for the idea run to read."""
    ins = insights_by_entry(cal)
    rows = []
    for e in cal["entries"]:
        if e["id"] in ins:
            rows.append({"date": e["date"], "type": e["media_type"], "title": e["idea"].get("title"),
                         "hook": e.get("hook"), "topic": e["idea"].get("topic"), "shape": e["idea"].get("shape"),
                         "series": e["idea"].get("series"), **ins[e["id"]]})
    p = DATA / "numbers_for_ideas.json"
    p.write_text(json.dumps({"fetched_at": json.loads(INSIGHTS.read_text()).get("_fetched_at") if INSIGHTS.exists() else None,
                             "posts": rows}, indent=1))
    return p


def _run_ideas(prompt: str, use: list[str], count: int) -> None:
    run = {"id": uuid.uuid4().hex[:8], "started": now_utc().isoformat(), "prompt": prompt, "use": use, "status": "running"}
    STATE["ideas_run"] = run
    try:
        pull()
        cal = load()
        nums = _numbers_digest(cal)
        hist = DATA / "ideas_history.json"
        d = _ideas()
        hist.write_text(json.dumps([{k: i.get(k) for k in ("title", "hook", "state", "reason")} for i in d["ideas"]], indent=1))
        task = (HERE / "ideas_prompt.md").read_text().format(
            count=count, today=date.today().isoformat(), numbers=nums, history=hist,
            prompt=prompt or "(none: pitch the strongest ideas you can find)",
            use_numbers="yes" if "numbers" in use else "no", use_trends="yes" if "trends" in use else "no",
            use_dates="yes" if "dates" in use else "no")
        tools = "Read,Glob,Grep" + (",WebSearch,WebFetch" if ("trends" in use or "dates" in use) else "")
        r = subprocess.run([CLAUDE, "-p", task, "--output-format", "json", "--allowedTools", tools,
                            "--disallowedTools", "Edit,Write,Bash,NotebookEdit", "--add-dir", str(DATA)],
                           cwd=AGENT, capture_output=True, text=True, timeout=1500)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip()[-500:] or r.stdout.strip()[-500:])
        text = json.loads(r.stdout).get("result", "")
        m = re.search(r"\{[\s\S]*\}\s*$", text.strip()) or re.search(r"```json\s*([\s\S]*?)```", text)
        payload = json.loads(m.group(1) if m and m.lastindex else m.group(0)) if m else {}
        new = payload.get("ideas", [])
        if not new:
            raise RuntimeError("The run finished without ideas: " + text[-300:])
        d = _ideas()
        for i in new:
            i.update(id=uuid.uuid4().hex[:10], state="new", run=run["id"], created=now_utc().isoformat())
            for n, a in enumerate(i.get("needs", [])):
                a["id"] = f"a{n + 1}"
        d["ideas"] = new + d["ideas"]
        run.update(status="done", finished=now_utc().isoformat(), n=len(new))
        d["runs"] = [run] + d.get("runs", [])[:30]
        _save_ideas(d)
    except Exception as exc:  # noqa: BLE001
        run.update(status="failed", error=str(exc)[:600], finished=now_utc().isoformat())
    STATE["ideas_run"] = run


@app.post("/api/ideas/run")
async def ideas_run(request: Request):
    body = await request.json()
    if STATE["ideas_run"] and STATE["ideas_run"].get("status") == "running":
        raise HTTPException(409, "Ideas are already being worked on.")
    use = [u for u in body.get("use", ["numbers", "trends", "dates"]) if u in ("numbers", "trends", "dates")]
    count = max(3, min(12, int(body.get("count") or 8)))
    threading.Thread(target=_run_ideas, args=((body.get("prompt") or "").strip()[:800], use, count), daemon=True).start()
    return {"ok": True}


@app.post("/api/ideas/{iid}/reject")
async def idea_reject(iid: str, request: Request):
    body = await request.json()
    d = _ideas()
    for i in d["ideas"]:
        if i["id"] == iid:
            i.update(state="rejected", reason=(body.get("reason") or "").strip()[:300])
            _save_ideas(d)
            return {"ok": True}
    raise HTTPException(404)


@app.post("/api/ideas/{iid}/accept")
async def idea_accept(iid: str, request: Request):
    body = await request.json()
    d = _ideas()
    idea = next((i for i in d["ideas"] if i["id"] == iid), None)
    if not idea:
        raise HTTPException(404)
    day = date.fromisoformat(body.get("date") or idea.get("suggested_date") or date.today().isoformat())
    kind = idea.get("media_type") or "reel"
    def fn(cal):
        replaced = []
        for e in cal["entries"]:
            if e["date"] == day.isoformat() and e["network"] == "instagram" and e["status"] == "planned":
                e.update(status="cut", cut_reason=f"Replaced by a Studio idea: {idea['title']}", cut_from="planned",
                         cut_at=now_utc().isoformat())
                replaced.append(e["idea"]["title"])
        base = f"{day.isoformat()}_in_idea"
        n = 1
        ids = {e["id"] for e in cal["entries"]}
        while f"{base}{n}" in ids:
            n += 1
        when = datetime(day.year, day.month, day.day, 10, tzinfo=CT).astimezone(timezone.utc).isoformat()
        script = idea.get("script") or []
        cal["entries"].append({
            "id": f"{base}{n}", "date": day.isoformat(), "network": "instagram", "media_type": kind,
            "when": when, "status": "planned",
            "idea": {"title": idea["title"], "hook": idea.get("hook", ""),
                     "brief": (idea.get("format", "") + ". " + " / ".join(script) + "\nWhy: " + idea.get("why", "")
                               + "\nSources: " + "; ".join(f"{s.get('name')} {s.get('url', '')}" for s in idea.get("sources", []))).strip(),
                     "topic": idea.get("topic"), "shape": "mouth_notes" if idea.get("series") == "Mouth Notes" else idea.get("shape", "reel"),
                     "hook_style": idea.get("hook_style", "statement"), "tone": "calm", "pillar": idea.get("pillar", "education"),
                     "media_type": kind, "calendar_ref": None, "slug": f"{base}{n}", "series": idea.get("series"),
                     "lane": idea.get("lane"), "sources": idea.get("sources", [])},
            "asks": [{"id": a["id"], "kind": a.get("kind", "photo"), "q": a.get("q", "")} for a in idea.get("needs", [])
                     if a.get("kind") in ("photo", "yesno")],
            "notes": [f"{_stamp()}: added from the Studio idea suggester."
                      + (f" Replaced: {', '.join(replaced)}." if replaced else "")],
        })
        return f"{base}{n}"
    new_id = mutate(f"add idea for {day.isoformat()}: {idea['title'][:60]}", fn)
    idea.update(state="accepted", entry=new_id)
    _save_ideas(d)
    return {"ok": True, "entry": new_id}


# ---- Instagram numbers (the encrypted ig-insights workflow, decrypted here) --------------
def _keypair() -> tuple[Path, Path]:
    priv, pub = KEYS / "priv.pem", KEYS / "pub.pem"
    if not priv.exists():
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:3072", "-out", str(priv)], check=True,
                       capture_output=True)
        os.chmod(priv, 0o600)
        subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)], check=True, capture_output=True)
    return priv, pub


def _refresh_insights() -> None:
    run = {"started": now_utc().isoformat(), "status": "running"}
    STATE["insights_run"] = run
    tmp = DATA / "ins_tmp"
    try:
        priv, pub = _keypair()
        b64 = base64.b64encode(pub.read_bytes()).decode()
        before = now_utc() - timedelta(seconds=5)
        subprocess.run(["gh", "workflow", "run", "ig-insights.yml", "--repo", GH_REPO, "-f", f"pubkey={b64}"], check=True,
                       capture_output=True, text=True)
        rid = None
        for _ in range(30):
            time.sleep(4)
            r = subprocess.run(["gh", "run", "list", "--repo", GH_REPO, "--workflow", "ig-insights.yml", "-L", "3",
                                "--json", "databaseId,createdAt"], capture_output=True, text=True)
            runs = [x for x in json.loads(r.stdout or "[]") if datetime.fromisoformat(x["createdAt"].replace("Z", "+00:00")) >= before]
            if runs:
                rid = str(runs[0]["databaseId"]); break
        if not rid:
            raise RuntimeError("The export run did not start.")
        w = subprocess.run(["gh", "run", "watch", rid, "--repo", GH_REPO, "--exit-status"], capture_output=True, text=True, timeout=900)
        if w.returncode != 0:
            raise RuntimeError("The export run failed on GitHub.")
        shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
        subprocess.run(["gh", "run", "download", rid, "--repo", GH_REPO, "-n", "ig-insights", "-D", str(tmp)], check=True,
                       capture_output=True)
        subprocess.run(["openssl", "pkeyutl", "-decrypt", "-inkey", str(priv), "-in", str(tmp / "key.enc"), "-out", str(tmp / "k.bin")],
                       check=True, capture_output=True)
        subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-in", str(tmp / "ins.enc"), "-out", str(tmp / "ins.json"),
                        "-pass", f"file:{tmp / 'k.bin'}"], check=True, capture_output=True)
        data = json.loads((tmp / "ins.json").read_text())
        data["_fetched_at"] = now_utc().isoformat()
        INSIGHTS.write_text(json.dumps(data))
        run.update(status="done", posts=len(data.get("media", [])))
    except Exception as exc:  # noqa: BLE001
        run.update(status="failed", error=str(exc)[:400])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        run["finished"] = now_utc().isoformat()
        STATE["insights_run"] = run


@app.post("/api/insights/refresh")
def insights_refresh():
    if STATE["insights_run"] and STATE["insights_run"].get("status") == "running":
        raise HTTPException(409, "Already fetching.")
    threading.Thread(target=_refresh_insights, daemon=True).start()
    return {"ok": True}


@app.on_event("startup")
def _start() -> None:
    threading.Thread(target=_puller, daemon=True).start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("STUDIO_PORT", "8797")), log_level="warning")
