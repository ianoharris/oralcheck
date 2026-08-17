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
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

import ideas

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
# Which connected Publora accounts a post goes to, in order. Override with a
# comma-separated list of platform prefixes to add or drop a network without
# touching code.
PUBLORA_PLATFORMS = os.environ.get("PUBLORA_PLATFORMS", "instagram")
# Sent on every Publora call. Default python client user agents get blocked by
# some edge configurations (Cloudflare returns "error code: 1010" to
# Python-urllib), and an identifiable agent is the polite default anyway.
PUBLORA_UA = "OralCheckBot/1.0 (+https://oralcheck.org)"
# Publora's Starter plan caps active scheduled posts at 3 counted per platform
# target, so Instagram alone fills it and LinkedIn cannot be added there. When
# this is on, an approved post also arrives in Telegram as a LinkedIn-ready
# package to drop into LinkedIn's own (free, unlimited) scheduler. Set to "0"
# once LinkedIn is published automatically.
LINKEDIN_HANDOFF = os.environ.get("LINKEDIN_HANDOFF", "1") != "0"
QUEUE_DIR         = Path(__file__).parent / "queue"
APPROVAL_TIMEOUT  = 21600  # 6 hours -- gives you the day to approve, not a rushed window


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

class _Log:
    """This module reports progress with print(); GitHub Actions captures stdout.
    Thin shim so the Publora code can read like the rest of the agent."""
    @staticmethod
    def info(msg, *a):
        print(msg % a if a else msg, flush=True)

    @staticmethod
    def warning(msg, *a):
        print("WARN: " + (msg % a if a else msg), flush=True)


log = _Log()


class PubloraError(RuntimeError):
    pass


class PubloraQuotaError(PubloraError):
    """Plan limit hit. Retrying cannot help, so the retry loop must not."""


def _publora_check(resp: httpx.Response, what: str) -> httpx.Response:
    """Raise with Publora's actual explanation attached.

    httpx's raise_for_status() reports only the status line, which is why the
    recurring "403 Forbidden on update-post" reports carried no reason at all
    and could not be diagnosed. The reason turned out to be a plan quota.
    """
    if resp.is_success:
        return resp
    try:
        payload = resp.json()
        body = json.dumps(payload)
    except Exception:
        payload, body = {}, resp.text

    if payload.get("code") == "SCHEDULED_POST_LIMIT_REACHED":
        raise PubloraQuotaError(
            "Publora will not accept another scheduled post: "
            f"{payload.get('message', '').strip()} "
            "Every platform a post targets counts separately, so three posts on "
            "two networks needs six slots. Either publish or delete something "
            "already scheduled, or raise the Publora plan."
        )

    raise PubloraError(f"Publora {resp.status_code} on {what}: {body[:600]}")


def _publora_platforms() -> list[str]:
    """Every connected platform we publish to, Instagram first.

    Previously hard-coded to the first instagram- connection, so the LinkedIn
    page could be connected in Publora and still never receive anything.
    """
    r = _publora_check(
        httpx.get(f"{PUBLORA_BASE}/platform-connections",
                  headers={"x-publora-key": PUBLORA_API_KEY, "User-Agent": PUBLORA_UA}, timeout=20),
        "platform-connections",
    )
    conns = r.json().get("connections", [])

    wanted = [p.strip() for p in PUBLORA_PLATFORMS.split(",") if p.strip()]
    ids: list[str] = []
    for prefix in wanted:
        for c in conns:
            pid = str(c.get("platformId", ""))
            if not pid.startswith(prefix + "-"):
                continue
            # A platform whose token has expired accepts the draft and then
            # fails at publish time, which is invisible until the post silently
            # never appears.
            if c.get("tokenStatus") not in (None, "valid"):
                log.warning("Skipping %s: tokenStatus=%s", pid, c.get("tokenStatus"))
                continue
            ids.append(pid)
    if not ids:
        raise PubloraError(
            f"No connected Publora account matched {wanted}. "
            f"Connected: {[c.get('platformId') for c in conns]}"
        )
    return ids


def _weekly_slots(n: int, start: datetime | None = None) -> list[datetime]:
    """n posting times spread across the coming week (evening slot, ~5pm CT).

    Spacing is computed over n-1 gaps, not n. Dividing by n left the last slot
    short of the end of the week and, combined with rounding, put two posts on
    the same day at the identical minute: n=7 produced days 1,2,3,4,4,5,6 and
    n=4 produced 1,3,4,5. Days are now assigned by even division and then
    de-duplicated, so no two posts ever collide.
    """
    base = start or datetime.now(timezone.utc)
    span = 6  # day 1 (tomorrow) through day 7
    POST_HOUR = 22  # ~5pm CT

    used: set[datetime] = set()
    slots = []
    for i in range(n):
        day = 1 + (round(i * span / (n - 1)) if n > 1 else 0)
        when = (base + timedelta(days=day)).replace(
            hour=POST_HOUR, minute=0, second=0, microsecond=0)
        # More posts than days is legitimate (a heavy week). Shift the hour
        # rather than stacking two posts on the same timestamp.
        while when in used:
            when += timedelta(hours=1)
        used.add(when)
        slots.append(when)
    return sorted(slots)


def post_via_publora(manifest: dict, media_files: list[Path],
                     when: datetime | None = None) -> str:
    """Create a Publora post, upload the media, and schedule it. Defaults to ~2
    minutes out; pass `when` to schedule it for a specific time (weekly spread).
    Returns the Publora post group id."""
    headers = {"x-publora-key": PUBLORA_API_KEY, "Content-Type": "application/json",
               "User-Agent": PUBLORA_UA}
    is_video = manifest["media_type"] in ("reel", "animated")
    mime = "video/mp4" if is_video else "image/jpeg"
    ext  = "mp4" if is_video else "jpg"
    typ  = "video" if is_video else "image"

    platforms = _publora_platforms()
    caption  = manifest.get("caption", "")
    hashtags = manifest.get("hashtags", [])
    full = caption + ("\n\n" + " ".join(f"#{h}" for h in hashtags) if hashtags else "")

    pr = _publora_check(
        httpx.post(f"{PUBLORA_BASE}/create-post", headers=headers,
                   json={"content": full, "platforms": platforms}, timeout=30),
        "create-post",
    )
    post_group_id = pr.json()["postGroupId"]
    log.info("Publora draft %s -> %s", post_group_id, ", ".join(platforms))

    for i, path in enumerate(media_files, 1):
        fn = f"oralcheck_{int(time.time())}_{i}.{ext}"
        ur = _publora_check(
            httpx.post(f"{PUBLORA_BASE}/get-upload-url", headers=headers,
                       json={"fileName": fn, "contentType": mime,
                             "postGroupId": post_group_id, "type": typ}, timeout=30),
            "get-upload-url",
        )
        upload_url = ur.json()["uploadUrl"]
        with open(path, "rb") as f:
            _publora_check(
                httpx.put(upload_url, content=f.read(),
                          headers={"Content-Type": mime}, timeout=180),
                f"upload {fn}",
            )
        # A carousel fires this loop up to 10 times back to back. Pace it a
        # little so a burst can't trip Publora's rate limiting, which is one of
        # the things that can surface later as a 403 on scheduling.
        if i < len(media_files):
            time.sleep(1.0)

    _publora_wait_for_media(post_group_id, len(media_files))

    # Cover goes on while the post is still a draft: attaching it needs an
    # update-post, and that re-runs the scheduled-post quota check once the post
    # is scheduled.
    if is_video and media_files:
        _set_reel_cover(post_group_id, media_files[0])

    when_dt = when or (datetime.now(timezone.utc) + timedelta(minutes=5))
    now = datetime.now(timezone.utc)
    if when_dt <= now + timedelta(minutes=2):
        # Publora rejects a scheduledTime that is already past or imminent, and
        # approval can land well after the slots were computed.
        when_dt = now + timedelta(minutes=5)
    when_str = when_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # The schedule call is the step that has been failing. Retry it: the failure
    # is intermittent (posts go out fine most days), which points at a
    # server-side race or rate limit rather than anything wrong with the post.
    last: Exception | None = None
    for attempt in range(4):
        try:
            _publora_check(
                httpx.put(f"{PUBLORA_BASE}/update-post/{post_group_id}", headers=headers,
                          json={"status": "scheduled", "scheduledTime": when_str}, timeout=30),
                f"update-post/{post_group_id}",
            )
            log.info("Scheduled %s for %s", post_group_id, when_str)
            return post_group_id
        except PubloraQuotaError:
            raise          # a quota will not clear by waiting
        except PubloraError as e:
            last = e
            wait = 5 * (2 ** attempt)
            log.warning("Schedule attempt %d failed (%s). Retrying in %ds.",
                        attempt + 1, e, wait)
            time.sleep(wait)

    # Out of retries. Say plainly that a draft is sitting in Publora with the
    # media attached, so it can be scheduled by hand instead of being lost.
    raise PubloraError(
        f"Could not schedule after 4 attempts. A draft with the media is in "
        f"Publora as {post_group_id} and can be scheduled manually. Last error: {last}"
    )


# Candidate cover times, in seconds. The opening scene now renders its headline
# from frame 0, but a fixed timestamp is brittle: it only takes a timing change
# to start shipping a blank cover, which is what older reels did (black at 0.0s,
# still empty at 0.45s, text only from ~1.0s). The best of these wins on merit.
COVER_CANDIDATES = (0.4, 0.8, 1.4, 2.2)


def _frame_content_score(path: Path) -> float:
    """How much is actually drawn on this frame.

    Standard deviation across the greyscale frame. A blank background is nearly
    uniform and scores near zero; a frame with a headline on it scores far
    higher. Good enough to never pick an empty cover, without needing to know
    anything about the animation's timing.
    """
    try:
        from PIL import Image, ImageStat
        with Image.open(path) as im:
            return ImageStat.Stat(im.convert("L")).stddev[0]
    except Exception:  # noqa: BLE001
        return 0.0


def _extract_cover_frame(video: Path) -> Path | None:
    """Pick the strongest early frame of the reel to use as its cover.

    Taken from the video itself rather than rendered separately, so the cover is
    a frame the viewer actually sees and cannot drift out of sync with it.
    """
    tmp = Path(tempfile.gettempdir())
    stamp = int(time.time())
    best: tuple[float, Path] | None = None
    made: list[Path] = []

    for i, t in enumerate(COVER_CANDIDATES):
        out = tmp / f"cover_{stamp}_{i}.jpg"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(t), "-i", str(video),
                 "-frames:v", "1", "-q:v", "2", str(out)],
                check=True, capture_output=True, timeout=60,
            )
        except FileNotFoundError:
            log.warning("ffmpeg not on PATH; skipping reel cover.")
            return None
        except Exception as exc:  # noqa: BLE001
            log.warning("Cover frame at %ss failed (%s).", t, exc)
            continue
        if not (out.exists() and out.stat().st_size > 0):
            continue
        made.append(out)
        score = _frame_content_score(out)
        log.info("Cover candidate %ss scored %.1f", t, score)
        if best is None or score > best[0]:
            best = (score, out)

    if best is None:
        return None
    for p in made:
        if p != best[1]:
            try:
                p.unlink()
            except OSError:
                pass
    log.info("Cover frame chosen (score %.1f).", best[0])
    return best[1]


def _set_reel_cover(post_group_id: str, video: Path) -> None:
    """Upload a cover for a Reel and attach it.

    Two steps: the upload returns a URL, and the URL only takes effect once it
    is written to platformSettings.instagram.coverUrl.

    Must run while the post is still a draft. Any update-post on an already
    scheduled post re-runs the plan's scheduled-post check, which fails once
    the quota is full, so doing this after scheduling would break publishing.
    """
    frame = _extract_cover_frame(video)
    if not frame:
        return
    try:
        with open(frame, "rb") as f:
            r = httpx.post(
                f"{PUBLORA_BASE}/upload-instagram-cover",
                headers={"x-publora-key": PUBLORA_API_KEY, "User-Agent": PUBLORA_UA},
                data={"postGroupId": post_group_id},
                files={"cover": (frame.name, f, "image/jpeg")},
                timeout=120,
            )
        _publora_check(r, "upload-instagram-cover")
        cover_url = r.json().get("url") or r.json().get("coverUrl")
        if not cover_url:
            log.warning("Cover uploaded but no URL returned; leaving default cover.")
            return

        _publora_check(
            httpx.put(
                f"{PUBLORA_BASE}/update-post/{post_group_id}",
                headers={"x-publora-key": PUBLORA_API_KEY, "Content-Type": "application/json",
                         "User-Agent": PUBLORA_UA},
                json={"platformSettings": {"instagram": {"coverUrl": cover_url}}},
                timeout=30,
            ),
            "update-post (coverUrl)",
        )
        log.info("Reel cover set from frame at %ss.", COVER_AT_SECONDS)
    except Exception as exc:  # noqa: BLE001
        # A missing cover is cosmetic. Never let it stop the post going out.
        log.warning("Could not set reel cover: %s", exc)
    finally:
        try:
            frame.unlink()
        except OSError:
            pass


def _publora_wait_for_media(post_group_id: str, expected: int, timeout_s: int = 90) -> None:
    """Wait for uploaded media to settle before scheduling.

    Publora validates media at the scheduling gate, so scheduling straight after
    the upload PUT is a race. Note its `status` field is not fully reliable: a
    post has been observed with all seven files fetchable at their media URLs
    while every one still read "uploading". So a stuck status is logged and
    allowed through rather than treated as fatal, and the retry loop around the
    schedule call is what actually absorbs the race.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = httpx.get(f"{PUBLORA_BASE}/get-post/{post_group_id}",
                          headers={"x-publora-key": PUBLORA_API_KEY, "User-Agent": PUBLORA_UA}, timeout=20)
            if not r.is_success:
                time.sleep(3)
                continue
            media = r.json().get("media", []) or []
            if len(media) < expected:
                time.sleep(3)
                continue
            failed = [m for m in media if m.get("status") == "failed"]
            if failed:
                raise PubloraError(
                    "Publora reported failed media: "
                    + ", ".join(f"{m.get('sourceFileName')}: {m.get('failureReason')}" for m in failed)
                )
            if all(m.get("status") != "uploading" for m in media):
                return
        except PubloraError:
            raise
        except Exception:
            pass
        time.sleep(3)
    log.warning("Media on %s still reads 'uploading' after %ds; scheduling anyway.",
                post_group_id, timeout_s)


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


LINKEDIN_SYSTEM = (
    "You rewrite social copy for LinkedIn. The brand is OralCheck, a free, private "
    "oral cancer risk screener built by Ian Harris, a predental student at the "
    "University of Wisconsin-Madison. Voice is calm, grounded and evidence-based: "
    "no hype, no exclamation points, no em dashes, and never flippant about the "
    "disease."
)


def _linkedin_caption(manifest: dict) -> str:
    """Rewrite the Instagram caption for LinkedIn.

    Not a copy-paste of the Instagram text. LinkedIn rewards a longer,
    professional register and punishes hashtag stuffing, and the audience skews
    toward clinicians, students and public-health people rather than patients.
    """
    ig = manifest.get("caption", "").strip()
    if not ig:
        return ""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return ig
    try:
        import anthropic
        msg = anthropic.Anthropic(api_key=key).messages.create(
            model=os.environ.get("CONTENT_MODEL", "claude-opus-4-8"),
            max_tokens=900,
            system=LINKEDIN_SYSTEM,
            messages=[{"role": "user", "content": (
                "Rewrite this Instagram caption as a LinkedIn post.\n"
                "- 90 to 160 words, short paragraphs with blank lines between them\n"
                "- Open with the single most surprising true fact, on its own line\n"
                "- Written for clinicians, dental students and public-health readers\n"
                "- Keep every number and claim exactly as given. Invent nothing.\n"
                "- End pointing to oralcheck.org\n"
                "- At most 3 hashtags, on the final line\n"
                "- Return only the post text.\n\n"
                f"{ig}"
            )}],
        )
        out = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text").strip()
        return out or ig
    except Exception as exc:  # noqa: BLE001
        log.warning("LinkedIn rewrite failed (%s); sending the Instagram caption.", exc)
        return ig


def _send_linkedin_handoff(manifest: dict, media_files: list[Path],
                           when: datetime | None) -> None:
    """Deliver a ready-to-post LinkedIn package to Telegram.

    Publora's Starter plan counts every platform target against a 3 scheduled
    post cap, so Instagram alone fills it. LinkedIn's own scheduler is free and
    takes posts up to 3 months out, so the fastest path is to hand over the copy
    and the image and schedule it there.
    """
    try:
        caption = _linkedin_caption(manifest)
        if not caption:
            return

        slot = when.strftime("%a %b %d, %-I%p UTC") if when else "whenever suits"
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text=(f"LinkedIn version, ready to schedule (suggested slot: {slot}).\n"
                 "Post as the OralCheck page, then use LinkedIn's own scheduler.\n"
                 "Caption is the next message so you can copy it cleanly."))
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=caption)

        # As a document, not a photo: Telegram re-compresses photos, and the
        # single image is what LinkedIn will actually display.
        if media_files:
            tg_upload("sendDocument", "document", str(media_files[0]),
                      chat_id=TELEGRAM_CHAT_ID,
                      caption="Image for the LinkedIn post (uncompressed).")
        if len(media_files) > 1:
            tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
               text=(f"This post has {len(media_files)} images. LinkedIn's native "
                     "scheduler does not accept multi-image posts, so either post "
                     "the first image alone or schedule it as a document carousel."))
    except Exception as exc:  # noqa: BLE001
        # Never let the handoff break an otherwise successful Instagram schedule.
        log.warning("LinkedIn handoff failed: %s", exc)


REJECT_REASON_TIMEOUT = 180  # seconds to type a reason before moving on

# Kept in the agent so there is one source of truth; imported lazily because
# this module is also run standalone.
def _help_text() -> str:
    try:
        from oralcheck_agent import HELP_TEXT
        return HELP_TEXT
    except Exception:
        return "Approve or Reject with the buttons. After a Reject, tell me why."


def _is_help(text: str) -> bool:
    return text.strip().lower().lstrip("/") in ("help", "?", "commands", "h")


def _collect_reject_reason(manifest: dict) -> str:
    """Ask why a post was rejected and wait briefly for a typed reply.

    Skipping is fine: silence after the timeout just means no reason, and the
    review carries on. Anything typed is kept and fed into the next round of
    idea generation, so a complaint only has to be made once.
    """
    global _UPDATE_OFFSET
    try:
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text=("Rejected. What was wrong with it? Reply in the next few minutes "
                 "and I'll apply it to future posts. Send \"skip\" or ignore this "
                 "to move on."))
    except Exception:
        return ""

    deadline = time.time() + REJECT_REASON_TIMEOUT
    while time.time() < deadline:
        params: dict = {"timeout": 20, "allowed_updates": '["message","callback_query"]'}
        if _UPDATE_OFFSET is not None:
            params["offset"] = _UPDATE_OFFSET
        try:
            r = httpx.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                          params=params, timeout=25)
            r.raise_for_status()
        except Exception:
            time.sleep(3)
            continue
        for update in r.json().get("result", []):
            _UPDATE_OFFSET = update["update_id"] + 1
            text = (update.get("message") or {}).get("text", "").strip()
            if not text:
                continue
            if _is_help(text):
                tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=_help_text())
                continue
            if text.lower() in ("skip", "no", "nothing", "-"):
                return ""
            tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
               text="Noted. I'll apply that from the next batch on.")
            return text[:400]
    return ""


def handle_decision(manifest: dict, item_dir: Path, decision: str,
                    when: datetime | None = None) -> bool:
    """Publish (approve) or discard (reject) a post. Returns True if it was
    approved and scheduled. `when` schedules it for a specific time."""
    if decision == "approve":
        print(f"Approved {manifest['id']}. Scheduling...", flush=True)
        media_files = [
            item_dir / f for f in manifest["files"]
            if f != "preview.jpg" and not f.endswith("_preview.jpg")
        ]
        try:
            if PUBLORA_API_KEY:
                pg = post_via_publora(manifest, media_files, when=when)
                when_txt = (f"scheduled for {when.strftime('%a %b %d, %-I%p UTC')}"
                            if when else "posting in ~2 minutes")
                tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
                   text=f"Approved and {when_txt} via Publora.\n(post {pg})")
                print(f"Publora scheduled: {pg} ({when})")
                if LINKEDIN_HANDOFF:
                    _send_linkedin_handoff(manifest, media_files, when)
            else:
                post_id = post_to_instagram(manifest, item_dir)
                if post_id in ("manual-video", "manual-no-ig"):
                    print(f"Manual upload required ({post_id}).")
                else:
                    tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=f"Posted to Instagram.\nPost ID: {post_id}")
        except Exception as exc:
            tg_err(f"Publish failed after approval: {exc}")
            shutil.rmtree(item_dir, ignore_errors=True)
            return False
        shutil.rmtree(item_dir, ignore_errors=True)
        return True
    # reject
    tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text="Rejected. I'll bring a replacement.")
    print(f"Rejected {manifest['id']}.")
    shutil.rmtree(item_dir, ignore_errors=True)
    return False


def _generate_replacement(ledger: dict):
    """Generate a fresh post from the next un-picked idea in the batch, so a
    rejection still leaves the target number of posts scheduled.

    Tries spare ideas in order: if one fails to generate, it's marked failed and
    the next is tried, rather than mistaking a generation error for "out of
    ideas". Returns (manifest, item_dir), or None only when the spare pool is
    genuinely exhausted."""
    import oralcheck_agent as agent   # lazy: heavy import, needs content-gen env

    while True:
        spares = ideas.spare_ideas(ledger)
        if not spares:
            return None                      # genuinely out of spare ideas
        idea = spares[0]
        idea["status"] = "selected"          # claim it so it isn't picked twice
        ideas.save_ledger(ledger)
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text=f"Building a replacement: \"{idea['title']}\" ({idea['media_type']})...")
        try:
            manifest = agent._queue_idea(idea)
        except Exception as exc:
            print(f"Replacement generation failed for {idea['id']}: {exc}", flush=True)
            manifest = None
        if manifest:
            ideas.mark_queued(ledger, idea["id"], manifest["id"])
            ideas.save_ledger(ledger)
            return manifest, QUEUE_DIR / manifest["id"]
        # generation failed -> don't burn the whole idea pool on one bad apple;
        # mark it failed (so spare_ideas skips it) and try the next spare.
        ideas.mark_failed(ledger, idea["id"])
        ideas.save_ledger(ledger)
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text="That one wouldn't build, trying the next idea...")


def review_batch() -> None:
    """Weekly review: send the picked posts, take approve/reject on each, and
    schedule approvals spread across the coming week. When a post is rejected,
    generate a replacement from the leftover ideas so the target number of posts
    still gets scheduled."""
    global _UPDATE_OFFSET
    pending = get_all_pending()
    if not pending:
        print("No pending posts in queue.")
        return

    ledger = ideas.load_ledger()
    target = len(pending)                 # however many were picked -> how many to schedule
    slots = _weekly_slots(target)
    approved = 0

    posts: dict[str, tuple[dict, Path]] = {}
    for i, (manifest, item_dir) in enumerate(pending, 1):
        if send_deck(manifest, item_dir, i, len(pending)):
            posts[manifest["id"]] = (manifest, item_dir)
    if not posts:
        return
    tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
       text=(f"{len(posts)} post(s) above. Approve the ones you want and I'll spread them across "
             f"the week. Reject any and I'll generate a replacement so {target} go out."))
    print(f"Sent {len(posts)} post(s) for review. Waiting for decisions...", flush=True)

    deadline = time.time() + APPROVAL_TIMEOUT
    while posts and approved < target and time.time() < deadline:
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
            msg_text = (update.get("message") or {}).get("text", "")
            if msg_text and _is_help(msg_text):
                tg("sendMessage", chat_id=TELEGRAM_CHAT_ID, text=_help_text())
                continue
            cb = update.get("callback_query", {})
            data = cb.get("data", "")
            for pid in list(posts):
                if data == f"approve_{pid}" or data == f"reject_{pid}":
                    try:
                        tg("answerCallbackQuery", callback_query_id=cb["id"])
                    except Exception:
                        pass
                    manifest, item_dir = posts.pop(pid)
                    if data.startswith("approve"):
                        when = slots[approved] if approved < len(slots) else None
                        if handle_decision(manifest, item_dir, "approve", when=when):
                            approved += 1
                    else:
                        handle_decision(manifest, item_dir, "reject")
                        idea = ideas.idea_for_manifest(ledger, pid)
                        # Ask why. A rejection with no reason teaches nothing, and
                        # the same kind of post comes back next week.
                        reason = _collect_reject_reason(manifest)
                        if reason:
                            ideas.record_feedback(
                                ledger,
                                reason,
                                title=manifest.get("hook") or manifest.get("caption", "")[:80],
                                media_type=manifest.get("media_type", ""),
                            )
                        if idea:
                            ideas.mark_rejected(ledger, idea["id"])
                        ideas.save_ledger(ledger)
                        # bring a replacement so `target` still get scheduled
                        repl = _generate_replacement(ledger)
                        if repl:
                            rm, rdir = repl
                            if send_deck(rm, rdir, len(posts) + approved + 1, target):
                                posts[rm["id"]] = (rm, rdir)
                        else:
                            tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
                               text=(f"I've used every idea in this week's batch, so I can't add "
                                     f"another replacement. {approved} of {target} are scheduled. "
                                     f"Run the idea flow again for a fresh set."))
                    break

    if approved >= target:
        tg("sendMessage", chat_id=TELEGRAM_CHAT_ID,
           text=f"Done. {approved} post(s) scheduled across the week.")
    for pid, (manifest, item_dir) in posts.items():
        shutil.rmtree(item_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    review_batch()


if __name__ == "__main__":
    main()
