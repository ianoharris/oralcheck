#!/usr/bin/env python3
"""
Telegram approval gate for OralCheck Instagram posts.
Reads the latest queued post, sends it to Telegram, waits for approval,
then posts to Instagram via Meta Graph API if approved. Runs inside GitHub Actions.
"""

import base64
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN    = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID  = os.environ["TELEGRAM_CHAT_ID"]
IMGBB_API_KEY     = os.environ.get("IMGBB_API_KEY", "")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")
IG_ACCESS_TOKEN   = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
GRAPH_BASE        = "https://graph.facebook.com/v21.0"
IG_CONFIGURED     = bool(IMGBB_API_KEY and INSTAGRAM_USER_ID and IG_ACCESS_TOKEN)
# Publora is the preferred publisher: the accounts are connected on Publora's side,
# so we never touch Meta Graph API tokens/permissions.
PUBLORA_API_KEY   = os.environ.get("PUBLORA_API_KEY", "")
PUBLORA_BASE      = "https://api.publora.com/api/v1"
QUEUE_DIR         = Path(__file__).parent / "queue"
APPROVAL_TIMEOUT  = 7200  # 2 hours


# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def tg(method: str, **kwargs) -> dict:
    resp = httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}",
        json=kwargs,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def tg_upload(method: str, field: str, file_path: str, **kwargs) -> dict:
    with open(file_path, "rb") as f:
        resp = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}",
            data=kwargs,
            files={field: f},
            timeout=120,
        )
    if not resp.is_success:
        print(f"Telegram {method} failed {resp.status_code}: {resp.text}", flush=True)
    resp.raise_for_status()
    return resp.json()


def tg_media_group(file_paths: list[str], caption: str | None = None) -> dict:
    """Send up to 10 images as a single album so the whole carousel is reviewable."""
    media = []
    files = {}
    handles = []
    try:
        for i, p in enumerate(file_paths[:10]):
            name = f"photo{i}"
            item = {"type": "photo", "media": f"attach://{name}"}
            if i == 0 and caption:
                item["caption"] = caption
            media.append(item)
            fh = open(p, "rb")
            handles.append(fh)
            files[name] = fh
        resp = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMediaGroup",
            data={"chat_id": TELEGRAM_CHAT_ID, "media": json.dumps(media)},
            files=files,
            timeout=180,
        )
    finally:
        for fh in handles:
            fh.close()
    if not resp.is_success:
        print(f"Telegram sendMediaGroup failed {resp.status_code}: {resp.text}", flush=True)
    resp.raise_for_status()
    return resp.json()


def tg_err(message: str) -> None:
    """Send an error notification to Telegram without raising."""
    try:
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=f"OralCheck pipeline error:\n{message}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

def get_latest_queued() -> tuple[dict, Path] | None:
    if not QUEUE_DIR.exists():
        return None
    dirs = sorted(
        [d for d in QUEUE_DIR.iterdir() if d.is_dir() and (d / "manifest.json").exists()],
        key=lambda d: d.name,
        reverse=True,
    )
    for d in dirs:
        manifest = json.loads((d / "manifest.json").read_text())
        if manifest.get("status") == "pending":
            return manifest, d
    return None


# ---------------------------------------------------------------------------
# Imgbb upload
# ---------------------------------------------------------------------------

def upload_to_imgbb(image_path: Path) -> str:
    image_b64 = base64.b64encode(image_path.read_bytes()).decode()
    resp = httpx.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMGBB_API_KEY, "image": image_b64},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Imgbb upload failed: {data}")
    return data["data"]["url"]


# ---------------------------------------------------------------------------
# Publora publishing (preferred — no Meta tokens needed)
# ---------------------------------------------------------------------------

def _publora_platform_id() -> str:
    r = httpx.get(f"{PUBLORA_BASE}/platform-connections",
                  headers={"x-publora-key": PUBLORA_API_KEY}, timeout=20)
    r.raise_for_status()
    for c in r.json().get("connections", []):
        if str(c.get("platformId", "")).startswith("instagram-"):
            return c["platformId"]
    raise RuntimeError("No Instagram account connected in Publora.")


def post_via_publora(manifest: dict, media_files: list[Path]) -> str:
    """Create a Publora post, upload the media, and schedule it to go live shortly.
    Returns the Publora post group id."""
    headers = {"x-publora-key": PUBLORA_API_KEY, "Content-Type": "application/json"}
    is_video = manifest["media_type"] in ("reel", "animated")
    mime = "video/mp4" if is_video else "image/jpeg"
    ext  = "mp4" if is_video else "jpg"
    typ  = "video" if is_video else "image"

    platform_id = _publora_platform_id()
    caption  = manifest.get("caption", "")
    hashtags = manifest.get("hashtags", [])
    full = caption + ("\n\n" + " ".join(f"#{h}" for h in hashtags) if hashtags else "")

    pr = httpx.post(f"{PUBLORA_BASE}/create-post", headers=headers,
                    json={"content": full, "platforms": [platform_id]}, timeout=30)
    pr.raise_for_status()
    post_group_id = pr.json()["postGroupId"]

    for i, path in enumerate(media_files, 1):
        fn = f"oralcheck_{int(time.time())}_{i}.{ext}"
        ur = httpx.post(f"{PUBLORA_BASE}/get-upload-url", headers=headers,
                        json={"fileName": fn, "contentType": mime,
                              "postGroupId": post_group_id, "type": typ}, timeout=30)
        ur.raise_for_status()
        upload_url = ur.json()["uploadUrl"]
        with open(path, "rb") as f:
            httpx.put(upload_url, content=f.read(),
                      headers={"Content-Type": mime}, timeout=180).raise_for_status()

    when = (datetime.now(timezone.utc) + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    sr = httpx.put(f"{PUBLORA_BASE}/update-post/{post_group_id}", headers=headers,
                   json={"status": "scheduled", "scheduledTime": when}, timeout=30)
    sr.raise_for_status()
    return post_group_id


# ---------------------------------------------------------------------------
# Meta Graph API helpers (legacy fallback)
# ---------------------------------------------------------------------------

def _ig_post(path: str, **params) -> dict:
    params["access_token"] = IG_ACCESS_TOKEN
    resp = httpx.post(f"{GRAPH_BASE}/{path}", params=params, timeout=30)
    if not resp.is_success:
        # Surface Meta's actual error (message/code/subcode), not just the status.
        # Strip the access token so it never lands in logs or Telegram.
        try:
            err = resp.json().get("error", {})
            detail = f"{err.get('message', resp.text)} (code {err.get('code')}, subcode {err.get('error_subcode')})"
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Graph API {resp.status_code} on /{path.split('/')[-1]}: {detail}")
    return resp.json()


def ig_create_image_container(image_url: str, caption: str | None = None, is_carousel_item: bool = False) -> str:
    params: dict = {
        "image_url": image_url,
        "is_carousel_item": "true" if is_carousel_item else "false",
    }
    if caption:
        params["caption"] = caption
    result = _ig_post(f"{INSTAGRAM_USER_ID}/media", **params)
    return result["id"]


def ig_create_carousel_container(child_ids: list[str], caption: str) -> str:
    result = _ig_post(
        f"{INSTAGRAM_USER_ID}/media",
        media_type="CAROUSEL",
        children=",".join(child_ids),
        caption=caption,
    )
    return result["id"]


def ig_wait_until_ready(creation_id: str, tries: int = 20, delay: float = 3.0) -> None:
    """Poll a media container until Instagram reports it FINISHED (ready to publish).

    Carousels in particular are often still IN_PROGRESS right after creation;
    publishing too early returns a 'media not ready' 400.
    """
    for _ in range(tries):
        resp = httpx.get(
            f"{GRAPH_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": IG_ACCESS_TOKEN},
            timeout=30,
        )
        status = resp.json().get("status_code") if resp.is_success else None
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Instagram container {creation_id} failed processing")
        time.sleep(delay)
    # Fall through and let publish attempt anyway (it will surface a clear error).


def ig_publish(creation_id: str) -> str:
    ig_wait_until_ready(creation_id)
    result = _ig_post(f"{INSTAGRAM_USER_ID}/media_publish", creation_id=creation_id)
    return result["id"]


# ---------------------------------------------------------------------------
# Instagram posting
# ---------------------------------------------------------------------------

def post_to_instagram(manifest: dict, item_dir: Path) -> str:
    media_type = manifest["media_type"]
    caption    = manifest["caption"]
    hashtags   = manifest.get("hashtags", [])
    full_caption = caption + ("\n\n" + " ".join(f"#{h}" for h in hashtags) if hashtags else "")

    if not IG_CONFIGURED:
        tg(
            "Post approved. Instagram not configured yet -- post manually.\n\n"
            f"Caption:\n{full_caption}"
        )
        return "manual-no-ig"

    media_files = [
        item_dir / f for f in manifest["files"]
        if f != "preview.jpg" and not f.endswith("_preview.jpg")
    ]

    # Video types require manual upload — the Reels API needs a video URL served
    # from a public CDN and a separate resumable upload flow; Imgbb only hosts images.
    if media_type in ("reel", "animated"):
        video_path = str(media_files[0]) if media_files else None
        note = f"Video post approved — upload manually.\n\nCaption:\n{full_caption}"
        if video_path:
            tg_upload("sendVideo", "video", video_path, chat_id=TELEGRAM_CHAT_ID, caption=note)
        else:
            tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=note)
        return "manual-video"

    if media_type == "carousel":
        child_ids: list[str] = []
        for img_path in media_files:
            img_url = upload_to_imgbb(img_path)
            child_id = ig_create_image_container(img_url, is_carousel_item=True)
            child_ids.append(child_id)
        container_id = ig_create_carousel_container(child_ids, full_caption)
        post_id = ig_publish(container_id)
        return post_id

    # Single image (image, infographic)
    img_url      = upload_to_imgbb(media_files[0])
    container_id = ig_create_image_container(img_url, caption=full_caption)
    post_id      = ig_publish(container_id)
    return post_id


# ---------------------------------------------------------------------------
# Approval polling
# ---------------------------------------------------------------------------

# Persistent getUpdates cursor shared across every review in this process. Advancing
# it past each processed update (rather than skipping to the latest with offset=-1)
# means a tap that arrives just before we poll is still in the queue and gets matched,
# instead of being swallowed as a "baseline" and lost.
_UPDATE_OFFSET: int | None = None


def wait_for_callback(manifest_id: str) -> str:
    """Long-poll Telegram for approve/reject on THIS post. Returns approve/reject/timeout.

    Matches by manifest_id, so callbacks for other/older posts are consumed and
    ignored rather than blocking. Never uses offset=-1 (which can skip a real tap).
    """
    global _UPDATE_OFFSET
    deadline = time.time() + APPROVAL_TIMEOUT
    print(f"Waiting up to {APPROVAL_TIMEOUT // 3600}h for approval of {manifest_id}...", flush=True)

    while time.time() < deadline:
        params: dict = {"timeout": 30, "allowed_updates": '["message","callback_query"]'}
        if _UPDATE_OFFSET is not None:
            params["offset"] = _UPDATE_OFFSET
        try:
            resp = httpx.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                params=params,
                timeout=35,
            )
            resp.raise_for_status()
        except Exception as exc:
            print(f"Poll error: {exc}", flush=True)
            time.sleep(5)
            continue

        for update in resp.json().get("result", []):
            _UPDATE_OFFSET = update["update_id"] + 1  # confirm/advance past it
            cb   = update.get("callback_query", {})
            data = cb.get("data", "")
            if data in (f"approve_{manifest_id}", f"reject_{manifest_id}"):
                try:
                    tg("answerCallbackQuery", callback_query_id=cb["id"])
                except Exception:
                    pass
                return "approve" if data.startswith("approve") else "reject"

    return "timeout"


# ---------------------------------------------------------------------------
# Review one item
# ---------------------------------------------------------------------------

def get_all_pending() -> list[tuple[dict, Path]]:
    if not QUEUE_DIR.exists():
        return []
    out = []
    for d in sorted(QUEUE_DIR.iterdir(), key=lambda d: d.name):
        if d.is_dir() and (d / "manifest.json").exists():
            manifest = json.loads((d / "manifest.json").read_text())
            if manifest.get("status") == "pending":
                out.append((manifest, d))
    return out


def send_deck(manifest: dict, item_dir: Path, index: int, total: int) -> bool:
    """Send one post's media + caption + Approve/Reject buttons. Returns True if sent."""
    media_files = [
        item_dir / f for f in manifest["files"]
        if f != "preview.jpg" and not f.endswith("_preview.jpg")
    ]
    if not media_files:
        print(f"No media files in {item_dir.name}.")
        return False

    is_video = manifest["media_type"] in ("reel", "animated")
    pillar   = (manifest.get("pillar") or "auto").replace("_", " ").title()
    caption  = manifest["caption"]
    hashtags = manifest.get("hashtags", [])
    full_caption = caption + ("\n\n" + " ".join(f"#{h}" for h in hashtags) if hashtags else "")

    slide_count = len(media_files)
    label = f"Post {index} of {total}\nPillar: {pillar}\n\n{manifest.get('hook', '')}"
    if is_video:
        tg_upload("sendVideo", "video", str(media_files[0]), chat_id=TELEGRAM_CHAT_ID, caption=label)
    elif manifest["media_type"] == "carousel" and slide_count > 1:
        tg_media_group([str(p) for p in media_files], caption=f"{label}\n\n({slide_count} slides, swipe to review all)")
    else:
        tg_upload("sendPhoto", "photo", str(media_files[0]), chat_id=TELEGRAM_CHAT_ID, caption=label)

    tg(
        "sendMessage",
        chat_id=TELEGRAM_CHAT_ID,
        text=f"*Post {index} of {total} — caption:*\n{full_caption}",
        parse_mode="Markdown",
        reply_markup={
            "inline_keyboard": [[
                {"text": "Approve", "callback_data": f"approve_{manifest['id']}"},
                {"text": "Reject",  "callback_data": f"reject_{manifest['id']}"},
            ]]
        },
    )
    return True


def handle_decision(manifest: dict, item_dir: Path, decision: str) -> None:
    if decision == "approve":
        print(f"Approved {manifest['id']}. Publishing...", flush=True)
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text=f"Approved \"{manifest.get('hook','')[:60]}\". Publishing to Instagram...")
        media_files = [
            item_dir / f for f in manifest["files"]
            if f != "preview.jpg" and not f.endswith("_preview.jpg")
        ]
        try:
            if PUBLORA_API_KEY:
                pg = post_via_publora(manifest, media_files)
                tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
                   text=f"Scheduled via Publora, it posts to Instagram in ~2 minutes.\n(post {pg})")
                print(f"Publora scheduled: {pg}")
            else:
                post_id = post_to_instagram(manifest, item_dir)
                if post_id in ("manual-video", "manual-no-ig"):
                    print(f"Manual upload required ({post_id}).")
                else:
                    tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=f"Posted to Instagram.\nPost ID: {post_id}")
        except Exception as exc:
            tg_err(f"Publish failed after approval: {exc}")
            shutil.rmtree(item_dir, ignore_errors=True)
            return
    else:  # reject
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text="Post rejected and discarded.")
        print(f"Rejected {manifest['id']}.")
    shutil.rmtree(item_dir, ignore_errors=True)


def review_batch() -> None:
    """Send every pending post at once, then accept approve/reject on any of them,
    in any order, until all are resolved or the window times out."""
    global _UPDATE_OFFSET
    pending = get_all_pending()
    if not pending:
        print("No pending posts in queue.")
        return

    posts: dict[str, tuple[dict, Path]] = {}
    for i, (manifest, item_dir) in enumerate(pending, 1):
        if send_deck(manifest, item_dir, i, len(pending)):
            posts[manifest["id"]] = (manifest, item_dir)
    if not posts:
        return
    tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
       text=f"{len(posts)} post(s) above, each with its own Approve / Reject. Tap on the ones you want.")
    print(f"Sent {len(posts)} post(s) for review. Waiting for decisions...", flush=True)

    deadline = time.time() + APPROVAL_TIMEOUT
    while posts and time.time() < deadline:
        # Must request callback_query explicitly: Telegram persists the last
        # allowed_updates, and an earlier message-only poll would otherwise drop taps.
        params: dict = {"timeout": 30, "allowed_updates": '["message","callback_query"]'}
        if _UPDATE_OFFSET is not None:
            params["offset"] = _UPDATE_OFFSET
        try:
            resp = httpx.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates", params=params, timeout=35)
            resp.raise_for_status()
        except Exception as exc:
            print(f"Poll error: {exc}", flush=True)
            time.sleep(5)
            continue
        for update in resp.json().get("result", []):
            _UPDATE_OFFSET = update["update_id"] + 1
            cb = update.get("callback_query", {})
            data = cb.get("data", "")
            for pid in list(posts):
                if data == f"approve_{pid}" or data == f"reject_{pid}":
                    try:
                        tg("answerCallbackQuery", callback_query_id=cb["id"])
                    except Exception:
                        pass
                    manifest, item_dir = posts.pop(pid)
                    handle_decision(manifest, item_dir, "approve" if data.startswith("approve") else "reject")
                    break

    for pid, (manifest, item_dir) in posts.items():
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=f"No response for \"{manifest.get('hook','')[:60]}\". Discarded.")
        shutil.rmtree(item_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    review_batch()


if __name__ == "__main__":
    main()
