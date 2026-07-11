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
# Meta Graph API helpers
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


def ig_publish(creation_id: str) -> str:
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

def wait_for_callback(manifest_id: str) -> str:
    """Long-poll Telegram for approve/reject. Returns 'approve', 'reject', or 'timeout'."""
    deadline = time.time() + APPROVAL_TIMEOUT
    last_update_id = None

    stale = httpx.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
        params={"offset": -1, "limit": 1},
        timeout=10,
    ).json().get("result", [])
    if stale:
        last_update_id = stale[-1]["update_id"]

    print(f"Waiting up to {APPROVAL_TIMEOUT // 3600}h for approval on Telegram...", flush=True)

    while time.time() < deadline:
        params: dict = {"timeout": 30, "allowed_updates": ["callback_query"]}
        if last_update_id is not None:
            params["offset"] = last_update_id + 1

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
            last_update_id = update["update_id"]
            cb   = update.get("callback_query", {})
            data = cb.get("data", "")
            if data in (f"approve_{manifest_id}", f"reject_{manifest_id}"):
                tg("answerCallbackQuery", callback_query_id=cb["id"])
                return "approve" if data.startswith("approve") else "reject"

    return "timeout"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    result = get_latest_queued()
    if not result:
        print("No pending posts in queue.")
        sys.exit(0)

    manifest, item_dir = result

    media_files = [
        item_dir / f for f in manifest["files"]
        if f != "preview.jpg" and not f.endswith("_preview.jpg")
    ]
    if not media_files:
        print("No media files in queue item.")
        sys.exit(1)

    is_video = manifest["media_type"] in ("reel", "animated")
    pillar   = (manifest.get("pillar") or "auto").replace("_", " ").title()
    caption  = manifest["caption"]
    hashtags = manifest.get("hashtags", [])
    full_caption = caption + ("\n\n" + " ".join(f"#{h}" for h in hashtags) if hashtags else "")

    method = "sendVideo" if is_video else "sendPhoto"
    field  = "video"     if is_video else "photo"
    tg_upload(
        method, field, str(media_files[0]),
        chat_id=TELEGRAM_CHAT_ID,
        caption=f"OralCheck post ready\nPillar: {pillar}\n\n{manifest.get('hook', '')}",
    )

    tg(
        "sendMessage",
        chat_id=TELEGRAM_CHAT_ID,
        text=f"*Caption:*\n{full_caption}",
        parse_mode="Markdown",
        reply_markup={
            "inline_keyboard": [[
                {"text": "Approve", "callback_data": f"approve_{manifest['id']}"},
                {"text": "Reject",  "callback_data": f"reject_{manifest['id']}"},
            ]]
        },
    )

    decision = wait_for_callback(manifest["id"])

    if decision == "approve":
        print("Approved. Posting to Instagram...", flush=True)
        try:
            post_id = post_to_instagram(manifest, item_dir)
        except Exception as exc:
            tg_err(f"Instagram post failed after approval: {exc}")
            raise
        if post_id in ("manual-video", "manual-no-ig"):
            print(f"Manual upload required ({post_id}).")
        else:
            tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=f"Posted to Instagram.\nPost ID: {post_id}")
            print(f"Done: {post_id}")
    elif decision == "reject":
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text="Post rejected and discarded.")
        print("Rejected.")
    else:
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text="No response in 2 hours. Post discarded.")
        print("Timed out.")

    shutil.rmtree(item_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
