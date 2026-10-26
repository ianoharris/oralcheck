"""
Publish to Instagram directly through Meta's API, instead of through Publora.

Publora's plan holds three scheduled posts at a time across every network,
which is what capped the feed. Meta's own limit is 100 API-published posts a
day per account, so Instagram goes direct and Publora keeps LinkedIn only.

Two differences from Publora shape how this is used:

- **Instagram's API cannot schedule.** A post is published the moment it is
  sent, so `post_calendar.py publish` runs every half hour and sends what is
  due (see .github/workflows/calendar.yml).
- **Meta fetches the media itself** from a public URL. Pictures go to Imgbb
  (as the old Graph API path did); a reel is fetched from the calendar's
  public GitHub release, with the redirect resolved first so Meta gets the
  file and not a redirect page.

Works with either kind of token: Instagram Login (graph.instagram.com, no
Facebook Page needed, the default) or Facebook Login (graph.facebook.com).
The publishing calls are the same on both; only the host differs.

Env: INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID, IMGBB_API_KEY,
     META_GRAPH_HOST (optional: graph.instagram.com | graph.facebook.com)

    python meta_ig.py check            # what the token can do; publishes nothing
    python meta_ig.py probe IMAGE.jpg RELEASE_ASSET.mp4   # Meta prepares both; nothing is published
    python meta_ig.py refresh --save   # refresh the token and store it as the repo secret
"""
from __future__ import annotations

import base64
import json
import logging
import os
import sys
import time
from pathlib import Path

import httpx

log = logging.getLogger("oralcheck.meta")
# httpx logs every request URL at INFO, and Meta's token rides in the query
# string. On a public repo the Actions log is public, so request logging stays
# off whenever this module is loaded (26 Oct: a bad secret showed up in one).
for _name in ("httpx", "httpcore"):
    logging.getLogger(_name).setLevel(logging.WARNING)

API_VERSION = "v26.0"
HOST = os.environ.get("META_GRAPH_HOST", "graph.instagram.com").strip() or "graph.instagram.com"
BASE = f"https://{HOST}/{API_VERSION}"
TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
IG_ID = os.environ.get("INSTAGRAM_USER_ID", "")
IMGBB_KEY = os.environ.get("IMGBB_API_KEY", "")
CAROUSEL_MAX = 20


class MetaError(RuntimeError):
    pass


def configured() -> bool:
    return bool(TOKEN and IG_ID and IMGBB_KEY)


def _err(r: httpx.Response, what: str) -> MetaError:
    # Meta's own message and code, never the token (it rides in the query string)
    try:
        e = r.json().get("error", {})
        detail = f"{e.get('message', '')} (code {e.get('code')}, subcode {e.get('error_subcode')})"
    except Exception:  # noqa: BLE001
        detail = r.text[:300]
    return MetaError(f"Meta {r.status_code} on {what}: {detail}")


def _post(path: str, **params) -> dict:
    r = httpx.post(f"{BASE}/{path}", data={**params, "access_token": TOKEN}, timeout=60)
    if not r.is_success:
        raise _err(r, path.split("/")[-1])
    return r.json()


def _get(path: str, **params) -> dict:
    r = httpx.get(f"{BASE}/{path}", params={**params, "access_token": TOKEN}, timeout=30)
    if not r.is_success:
        raise _err(r, path.split("/")[-1] or path)
    return r.json()


# --- public URLs for Meta to fetch -----------------------------------------

def host_image(path: Path, expire_s: int = 7 * 24 * 3600) -> str:
    """Upload a JPEG to Imgbb and return its direct URL. Instagram takes JPEG only."""
    r = httpx.post("https://api.imgbb.com/1/upload",
                   data={"key": IMGBB_KEY, "image": base64.b64encode(path.read_bytes()).decode(),
                         "expiration": str(expire_s)}, timeout=120)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if not r.is_success or not data.get("success"):
        raise MetaError(f"Imgbb upload of {path.name} failed ({r.status_code})")
    return data["data"]["url"]


def release_url(repo: str, tag: str, asset: str) -> str:
    """The direct URL of a public release asset. GitHub answers the download link
    with a redirect to a short-lived signed URL; Meta is given that URL."""
    url = f"https://github.com/{repo}/releases/download/{tag}/{asset}"
    r = httpx.head(url, follow_redirects=False, timeout=30)
    if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
        return r.headers["location"]
    if r.is_success:
        return url
    raise MetaError(f"Release asset {asset} not reachable ({r.status_code})")


# --- containers and publishing ---------------------------------------------

def wait_ready(container: str, timeout_s: int = 300, every: float = 5.0) -> None:
    """Poll a container until Meta has processed it. Reels take a minute or two."""
    t0 = time.time()
    status = None
    while time.time() - t0 < timeout_s:
        status = _get(container, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            info = _get(container, fields="status").get("status", "")
            raise MetaError(f"Container {container} {status}: {info}")
        time.sleep(every)
    raise MetaError(f"Container {container} still {status} after {timeout_s}s")


def publish_container(container: str) -> str:
    wait_ready(container)
    return _post(f"{IG_ID}/media_publish", creation_id=container)["id"]


def image_container(url: str, caption: str | None = None, carousel_item: bool = False) -> str:
    params = {"image_url": url}
    if carousel_item:
        params["is_carousel_item"] = "true"
    if caption is not None:
        params["caption"] = caption
    return _post(f"{IG_ID}/media", **params)["id"]


def post_image(path: Path, caption: str) -> str:
    return publish_container(image_container(host_image(path), caption))


def post_carousel(paths: list[Path], caption: str) -> str:
    if not 2 <= len(paths) <= CAROUSEL_MAX:
        raise MetaError(f"A carousel takes 2 to {CAROUSEL_MAX} pictures, not {len(paths)}")
    children = [image_container(host_image(p), carousel_item=True) for p in paths]
    for c in children:
        wait_ready(c, timeout_s=120, every=3)
    box = _post(f"{IG_ID}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)["id"]
    return publish_container(box)


def post_reel(video_url: str, caption: str, cover: Path | None = None) -> str:
    params = {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"}
    if cover:
        try:
            params["cover_url"] = host_image(cover)
        except MetaError as e:            # a missing cover is not worth a missing post
            log.warning("%s; using the first frame as the cover.", e)
    return publish_container(_post(f"{IG_ID}/media", **params)["id"])


def full_caption(manifest: dict) -> str:
    """The caption as posted: text, then the hashtags. Instagram caps a caption
    at 2,200 characters and 30 hashtags."""
    tags = manifest.get("hashtags", [])[:30]
    text = manifest.get("caption", "") + ("\n\n" + " ".join(f"#{h}" for h in tags) if tags else "")
    if len(text) > 2200:
        raise MetaError(f"Caption is {len(text)} characters; Instagram allows 2,200")
    return text


def usage() -> dict:
    """Posts published through the API in the last 24 hours, against the quota."""
    d = _get(f"{IG_ID}/content_publishing_limit", fields="quota_usage,config")
    row = (d.get("data") or [{}])[0]
    return {"used": row.get("quota_usage"), "total": (row.get("config") or {}).get("quota_total")}


def refresh() -> dict:
    """Refresh a long-lived Instagram Login token (valid 60 days from now).
    Returns {access_token, expires_in}. Facebook Login tokens do not use this."""
    r = httpx.get("https://graph.instagram.com/refresh_access_token",
                  params={"grant_type": "ig_refresh_token", "access_token": TOKEN}, timeout=30)
    if not r.is_success:
        raise _err(r, "refresh_access_token")
    return r.json()


def refresh_and_store(secret: str = "INSTAGRAM_ACCESS_TOKEN") -> int:
    """Refresh the token and write it back to the repo secret it came from, so
    it never reaches 60 days. Needs GH_TOKEN with permission to set secrets
    (a fine-grained token, Secrets: read and write, on this repo only); the
    workflow's own token cannot write secrets. Returns days of life left."""
    import subprocess
    new = refresh()
    subprocess.run(["gh", "secret", "set", secret], input=new["access_token"], text=True,
                   check=True, capture_output=True)
    return int(new.get("expires_in", 0)) // 86400


def check() -> int:
    """Report what the token can do, publishing nothing. Prints no secrets."""
    if not (TOKEN and IG_ID):
        print("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID.")
        return 1
    print(f"Host: {HOST}")
    ok = True
    try:
        fields = "username,account_type" if HOST == "graph.instagram.com" else "username,name"
        me = _get(IG_ID, fields=fields)
        print(f"Account: @{me.get('username')} ({me.get('account_type', 'business')})")
    except MetaError as e:
        print(f"Account lookup failed: {e}"); ok = False
    try:
        u = usage()
        print(f"Publishing quota: {u['used']} of {u['total']} used in the last 24 hours")
    except MetaError as e:
        print(f"Quota check failed (this is the call that needs publish permission): {e}"); ok = False
    print("Imgbb key: " + ("set" if IMGBB_KEY else "MISSING (pictures cannot be hosted)"))
    print("Ready to publish." if ok and IMGBB_KEY else "Not ready; see above.")
    return 0 if ok and IMGBB_KEY else 1


def probe(image: Path, reel_asset: str, repo: str = "ianoharris/oralcheck",
          tag: str = "calendar-2026-fall") -> int:
    """Have Meta fetch and process one picture and one reel the way a real post
    would, then stop short of publishing. Unpublished containers expire on
    their own after a day. This is the test to pass before IG_DIRECT goes on."""
    ok = True
    for what, make in (("picture", lambda: image_container(host_image(image), "probe")),
                       ("reel", lambda: _post(f"{IG_ID}/media", media_type="REELS", caption="probe",
                                              video_url=release_url(repo, tag, reel_asset))["id"])):
        try:
            c = make(); wait_ready(c)
            print(f"{what}: Meta fetched and processed it (container {c}, not published)")
        except MetaError as e:
            print(f"{what}: FAILED: {e}"); ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        sys.exit(check())
    if cmd == "probe":
        sys.exit(probe(Path(sys.argv[2]), sys.argv[3]))
    if cmd == "refresh":
        if "--save" in sys.argv:
            print(f"Token refreshed and stored; valid {refresh_and_store()} days.")
        else:
            print(json.dumps({"expires_in": refresh().get("expires_in")}))   # the token itself is never printed
        sys.exit(0)
    print(__doc__); sys.exit(2)
