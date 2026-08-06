#!/usr/bin/env python3
"""
OralCheck Review Server
Local FastAPI server for reviewing, editing, and approving queued Instagram posts.

Usage:
    python3.11 review_server.py
    then open http://localhost:8765
"""

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from oralcheck_agent import QUEUE_DIR, publora_post

app = FastAPI(title="OralCheck Review Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def _load_manifest(item_id: str) -> dict:
    p = QUEUE_DIR / item_id / "manifest.json"
    if not p.exists():
        raise HTTPException(404, f"Item not found: {item_id}")
    with open(p) as f:
        return json.load(f)


def _save_manifest(item_id: str, manifest: dict) -> None:
    p = QUEUE_DIR / item_id / "manifest.json"
    with open(p, "w") as f:
        json.dump(manifest, f, indent=2)


def _list_pending() -> list[dict]:
    if not QUEUE_DIR.exists():
        return []
    items = []
    for d in sorted(QUEUE_DIR.iterdir(), reverse=True):
        mp = d / "manifest.json"
        if mp.exists():
            with open(mp) as f:
                m = json.load(f)
            if m.get("status") == "pending":
                items.append(m)
    return items


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/queue")
def list_queue():
    return {"items": _list_pending()}


@app.get("/api/queue/{item_id}")
def get_item(item_id: str):
    return _load_manifest(item_id)


class EditRequest(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[list[str]] = None


@app.patch("/api/queue/{item_id}")
def edit_item(item_id: str, body: EditRequest):
    manifest = _load_manifest(item_id)
    if manifest["status"] != "pending":
        raise HTTPException(400, "Can only edit pending items")
    if body.caption is not None:
        manifest["caption"] = body.caption
    if body.hashtags is not None:
        manifest["hashtags"] = [h.lower().strip().lstrip("#") for h in body.hashtags]
    _save_manifest(item_id, manifest)
    return {"ok": True}


class ApproveRequest(BaseModel):
    schedule_minutes: int = 5


@app.post("/api/queue/{item_id}/approve")
def approve_item(item_id: str, body: ApproveRequest):
    manifest = _load_manifest(item_id)
    if manifest["status"] != "pending":
        raise HTTPException(400, "Can only approve pending items")

    item_dir = QUEUE_DIR / item_id
    media_type = manifest["media_type"]

    local_files = [
        str(item_dir / f)
        for f in manifest["files"]
        if f != "preview.jpg"
    ]

    if not local_files:
        raise HTTPException(400, "No media files found in queue item")

    schedule_at = datetime.now(timezone.utc) + timedelta(minutes=body.schedule_minutes)

    try:
        result = publora_post(
            caption=manifest["caption"],
            hashtags=manifest["hashtags"],
            local_paths=local_files,
            media_type=media_type,
            schedule_at=schedule_at,
        )
    except Exception as e:
        raise HTTPException(500, f"Publora error: {e}")

    manifest["status"] = "approved"
    manifest["approved_at"] = datetime.now(timezone.utc).isoformat()
    manifest["post_group_id"] = result.get("postGroupId", "")
    manifest["scheduled_for"] = schedule_at.isoformat()
    _save_manifest(item_id, manifest)

    return {"ok": True, "postGroupId": result.get("postGroupId")}


@app.delete("/api/queue/{item_id}")
def reject_item(item_id: str):
    manifest = _load_manifest(item_id)
    manifest["status"] = "rejected"
    manifest["rejected_at"] = datetime.now(timezone.utc).isoformat()
    _save_manifest(item_id, manifest)
    return {"ok": True}


@app.get("/media/{item_id}/{filename}")
def serve_media(item_id: str, filename: str):
    p = QUEUE_DIR / item_id / filename
    if not p.exists():
        raise HTTPException(404, "File not found")
    ext = p.suffix.lower()
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".mp4": "video/mp4",
    }
    return FileResponse(str(p), media_type=content_type_map.get(ext, "application/octet-stream"))


# ---------------------------------------------------------------------------
# HTML UI
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>OralCheck Review</title>
<style>
  :root {
    --bg:      #0d1a1b;
    --surface: #162628;
    --border:  #1e3436;
    --teal:    #0d7377;
    --teal-lt: #14a8ae;
    --coral:   #e8634a;
    --text:    #e8e4de;
    --muted:   #5a7476;
    --green:   #2eb87e;
    --red:     #e85a4a;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.55;
    min-height: 100vh;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 28px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 10;
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: var(--teal-lt);
    letter-spacing: -0.3px;
  }
  .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--coral); }
  .meta { color: var(--muted); font-size: 13px; }
  #refresh-btn {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: border-color 0.15s;
  }
  #refresh-btn:hover { border-color: var(--teal); }
  main { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
  #empty { color: var(--muted); text-align: center; padding: 80px 0; font-size: 16px; }
  .queue-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .card-media { position: relative; background: #0a1314; }
  .card-media img.single { width: 100%; display: block; aspect-ratio: 1; object-fit: cover; }
  .card-media video { width: 100%; display: block; aspect-ratio: 9/16; object-fit: contain; background: #0a1314; }
  .slide-strip {
    display: grid;
    gap: 2px;
    background: #0a1314;
  }
  .slide-strip img { width: 100%; display: block; object-fit: cover; }
  .media-type-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(13,26,27,0.85);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--teal-lt);
  }

  .card-body { padding: 18px; flex: 1; display: flex; flex-direction: column; gap: 12px; }
  .hook { font-size: 15px; font-weight: 600; color: var(--text); }
  .pillar-tag {
    display: inline-block;
    background: rgba(13,115,119,0.15);
    border: 1px solid rgba(13,115,119,0.3);
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
    color: var(--teal-lt);
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }
  .field-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  textarea, input[type="text"] {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    padding: 10px 12px;
    resize: vertical;
    transition: border-color 0.15s;
  }
  textarea:focus, input[type="text"]:focus { outline: none; border-color: var(--teal); }
  textarea { min-height: 90px; }

  .card-actions { display: flex; flex-direction: column; gap: 8px; padding: 0 18px 18px; }
  .schedule-row { display: flex; align-items: center; gap: 8px; }
  .schedule-row label { font-size: 13px; color: var(--muted); white-space: nowrap; }
  select {
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    flex: 1;
  }
  .btn-row { display: flex; gap: 8px; }
  .btn {
    flex: 1;
    padding: 10px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .btn:hover { opacity: 0.85; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-approve { background: var(--teal); color: #fff; }
  .btn-reject { background: var(--surface); border: 1px solid var(--border); color: var(--muted); }
  .btn-download { background: transparent; border: 1px solid var(--teal); color: var(--teal-lt); text-decoration: none; display: block; text-align: center; padding: 10px; border-radius: 8px; font-size: 14px; font-weight: 500; transition: background 0.15s; }
  .btn-download:hover { background: rgba(13,115,119,0.12); }
  .status-msg {
    font-size: 12px;
    text-align: center;
    padding: 4px;
    border-radius: 5px;
    font-weight: 500;
  }
  .status-ok { background: rgba(46,184,126,0.15); color: var(--green); }
  .status-err { background: rgba(232,90,74,0.12); color: var(--red); }
</style>
</head>
<body>
<header>
  <div class="logo">
    <div class="dot"></div>
    OralCheck Review
  </div>
  <div class="meta" id="queue-count">Loading...</div>
  <button id="refresh-btn" onclick="loadQueue()">Refresh</button>
</header>
<main>
  <div id="queue-grid" class="queue-grid"></div>
  <div id="empty" style="display:none">No pending posts. Run the agent to generate content.</div>
</main>

<script>
const SCHEDULE_OPTIONS = [
  {label: "2 minutes", value: 2},
  {label: "15 minutes", value: 15},
  {label: "1 hour", value: 60},
  {label: "4 hours", value: 240},
  {label: "Tomorrow (18 hr)", value: 1080},
];

function mediaUrl(id, filename) {
  return `/media/${id}/${filename}`;
}

function buildMediaSection(item) {
  const mt = item.media_type;
  const files = item.files.filter(f => f !== "preview.jpg");

  if (mt === "reel") {
    const vid = files.find(f => f.endsWith(".mp4"));
    return `
      <div class="card-media">
        <span class="media-type-badge">Reel</span>
        <video controls playsinline muted src="${mediaUrl(item.id, vid)}"></video>
      </div>`;
  }

  if (mt === "carousel") {
    const imgs = files.filter(f => !f.endsWith(".mp4"));
    const cols = Math.min(imgs.length, 4);
    const thumbs = imgs.map((f, i) =>
      `<img src="${mediaUrl(item.id, f)}" alt="Slide ${i+1}" loading="lazy" />`
    ).join("");
    return `
      <div class="card-media">
        <span class="media-type-badge">Carousel · ${imgs.length} slides</span>
        <div class="slide-strip" style="grid-template-columns: repeat(${cols}, 1fr);">
          ${thumbs}
        </div>
      </div>`;
  }

  // static image
  const img = files[0];
  return `
    <div class="card-media">
      <span class="media-type-badge">Image</span>
      <img class="single" src="${mediaUrl(item.id, img)}" alt="Post" loading="lazy" />
    </div>`;
}

function buildCard(item) {
  const mt = item.media_type;
  const files = (item.files || []).filter(f => f !== "preview.jpg");
  const schedOpts = SCHEDULE_OPTIONS.map((o, i) =>
    `<option value="${o.value}"${i === 0 ? " selected" : ""}>${o.label}</option>`
  ).join("");

  const tags = (item.hashtags || []).map(h => "#" + h).join(" ");

  return `
    <div class="card" id="card-${item.id}">
      ${buildMediaSection(item)}
      <div class="card-body">
        ${item.pillar ? `<div><span class="pillar-tag">${item.pillar.replace(/_/g, " ")}</span></div>` : ""}
        <div class="hook">${escHtml(item.hook || "")}</div>

        <div>
          <div class="field-label">Caption</div>
          <textarea id="caption-${item.id}">${escHtml(item.caption || "")}</textarea>
        </div>

        <div>
          <div class="field-label">Hashtags (space-separated)</div>
          <input type="text" id="hashtags-${item.id}" value="${escHtml(tags)}" />
        </div>
      </div>
      <div class="card-actions">
        ${mt === "reel" ? `<a class="btn btn-download" href="${mediaUrl(item.id, files.find(f => f.endsWith('.mp4')))}" download="oralcheck_reel.mp4">Download for Reels (add audio in app)</a>` : ""}
        <div class="schedule-row">
          <label>Schedule:</label>
          <select id="sched-${item.id}">${schedOpts}</select>
        </div>
        <div class="btn-row">
          <button class="btn btn-approve" onclick="approve('${item.id}')">${mt === "reel" ? "Post without audio" : "Approve & Schedule"}</button>
          <button class="btn btn-reject" onclick="reject('${item.id}')">Reject</button>
        </div>
        <div id="msg-${item.id}" class="status-msg" style="display:none"></div>
      </div>
    </div>`;
}

function escHtml(s) {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function showMsg(id, text, ok) {
  const el = document.getElementById("msg-" + id);
  el.textContent = text;
  el.className = "status-msg " + (ok ? "status-ok" : "status-err");
  el.style.display = "block";
}

async function approve(id) {
  const caption  = document.getElementById("caption-" + id).value;
  const hashText = document.getElementById("hashtags-" + id).value;
  const hashtags = hashText.trim().split(/\s+/).filter(Boolean).map(h => h.replace(/^#/, ""));
  const mins     = parseInt(document.getElementById("sched-" + id).value);

  const btn = document.querySelector(`#card-${id} .btn-approve`);
  btn.disabled = true;
  btn.textContent = "Posting...";

  try {
    // Save edits first
    await fetch(`/api/queue/${id}`, {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({caption, hashtags}),
    });

    // Approve
    const res = await fetch(`/api/queue/${id}/approve`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({schedule_minutes: mins}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unknown error");

    showMsg(id, "Scheduled. Post group: " + (data.postGroupId || "—"), true);
    setTimeout(() => {
      document.getElementById("card-" + id).style.opacity = "0.4";
      document.getElementById("card-" + id).style.pointerEvents = "none";
    }, 1200);
  } catch(e) {
    showMsg(id, "Error: " + e.message, false);
    btn.disabled = false;
    btn.textContent = "Approve & Schedule";
  }
}

async function reject(id) {
  if (!confirm("Reject and remove this post?")) return;
  const res = await fetch(`/api/queue/${id}`, {method: "DELETE"});
  if (res.ok) {
    document.getElementById("card-" + id).remove();
    await loadQueue();
  }
}

async function loadQueue() {
  try {
    const res = await fetch("/api/queue");
    const data = await res.json();
    const items = data.items || [];
    const countEl = document.getElementById("queue-count");
    const grid = document.getElementById("queue-grid");
    const empty = document.getElementById("empty");

    countEl.textContent = items.length + " pending";
    if (items.length === 0) {
      grid.innerHTML = "";
      empty.style.display = "block";
    } else {
      empty.style.display = "none";
      grid.innerHTML = items.map(buildCard).join("");
    }
  } catch(e) {
    console.error("Load failed:", e);
  }
}

loadQueue();
setInterval(loadQueue, 30000);
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
