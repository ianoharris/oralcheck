#!/usr/bin/env python3
"""
Diagnose the Instagram Graph API access token used for auto-posting.

Reports the token's scopes, type, and expiry, and the connected IG account type,
so we can see why publishing returns "(#10) Application does not have permission".
Prints NO secrets — only permission names and account metadata.

Env: INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID
"""

import os
import sys

import httpx

GRAPH = "https://graph.facebook.com/v21.0"
TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
IG_ID = os.environ.get("INSTAGRAM_USER_ID", "")

REQUIRED_SCOPES = [
    "instagram_basic",
    "instagram_content_publish",
    "pages_read_engagement",
    "pages_show_list",
    "business_management",
]


def main() -> int:
    if not TOKEN or not IG_ID:
        print("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID.")
        return 1

    # 1. Token debug: scopes + expiry + type
    print("=== Token ===")
    r = httpx.get(f"{GRAPH}/debug_token",
                  params={"input_token": TOKEN, "access_token": TOKEN}, timeout=30)
    data = r.json().get("data", {}) if r.is_success else {}
    if not data:
        print(f"  debug_token failed: {r.status_code} {r.text[:200]}")
    else:
        scopes = data.get("scopes", []) or data.get("granular_scopes", [])
        flat = scopes if scopes and isinstance(scopes[0], str) else \
               [g.get("scope") for g in scopes] if scopes else []
        print(f"  type: {data.get('type')}")
        print(f"  app_id: {data.get('app_id')}")
        print(f"  valid: {data.get('is_valid')}")
        exp = data.get("expires_at")
        print(f"  expires_at: {exp} ({'never' if exp == 0 else 'set'})")
        print(f"  scopes: {', '.join(flat) if flat else '(none reported)'}")
        print("\n=== Required scopes for publishing ===")
        for s in REQUIRED_SCOPES:
            have = s in flat
            print(f"  [{'OK ' if have else 'MISSING'}] {s}")

    # 2. IG account type
    print("\n=== Instagram account ===")
    r2 = httpx.get(f"{GRAPH}/{IG_ID}",
                   params={"fields": "username,account_type,name", "access_token": TOKEN}, timeout=30)
    if r2.is_success:
        acct = r2.json()
        print(f"  username: {acct.get('username')}")
        print(f"  account_type: {acct.get('account_type')}  (must be BUSINESS or CREATOR)")
    else:
        print(f"  lookup failed: {r2.status_code} {r2.text[:200]}")

    print("\nIf instagram_content_publish is MISSING or account_type is not BUSINESS/CREATOR,"
          " that is why publishing is denied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
