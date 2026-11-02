"use client";

import { useSyncExternalStore } from "react";
import { GoogleAnalytics } from "@next/third-parties/google";

const FLAG = "oralcheck:notrack";

/**
 * Whether this browser should report to Google Analytics. Only oralcheck.org
 * counts: dev servers shared the live property and were 376 of 1,321
 * pageviews in the 90 days to 30 Oct 2026. A browser opened once with
 * ?notrack=1 stops counting itself (Ian's own devices); ?notrack=0 undoes it.
 */
function shouldTrack(): boolean {
  try {
    const q = new URLSearchParams(window.location.search).get("notrack");
    if (q === "1") localStorage.setItem(FLAG, "1");
    if (q === "0") localStorage.removeItem(FLAG);
    if (localStorage.getItem(FLAG) === "1") return false;
  } catch {}
  return /(^|\.)oralcheck\.org$/.test(window.location.hostname);
}

const noop = () => () => {};

// The tag only mounts once the browser has said yes. This replaced an inline
// script that set GA's disable flag before gtag loaded: it did not run on 404
// pages, which render the layout on the client, so the opt-out leaked there.
// useSyncExternalStore renders nothing on the server and decides on the
// client without a hydration mismatch.
export default function AnalyticsGate({ gaId }: { gaId: string }) {
  const track = useSyncExternalStore(noop, shouldTrack, () => false);
  return track ? <GoogleAnalytics gaId={gaId} /> : null;
}
