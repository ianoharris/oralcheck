import { NextResponse } from "next/server";
import { checkRateLimit, getIp } from "@/lib/rateLimit";

// Free geocoding via OpenStreetMap Nominatim (no API key, no billing).
// Usage policy: send a descriptive User-Agent and keep volume modest.
type NominatimResult = {
  lat: string;
  lon: string;
  display_name: string;
};

export async function GET(request: Request) {
  // This was the one unmetered proxy on the site. Nominatim is free but its
  // usage policy is per-application, so sustained abuse through here gets
  // oralcheck.org blocked from OSM geocoding, taking Find Care down with it.
  const { allowed, resetMs } = checkRateLimit(`geocode:${getIp(request)}`, 20);
  if (!allowed) {
    return NextResponse.json(
      { error: "Too many requests" },
      { status: 429, headers: { "Retry-After": String(Math.ceil(resetMs / 1000)) } },
    );
  }

  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q");

  if (!q || !q.trim()) {
    return NextResponse.json(
      { error: "q query parameter is required" },
      { status: 400 },
    );
  }
  // Cap the length before forwarding. An unbounded query is passed straight to
  // a third party under our application name.
  if (q.length > 200) {
    return NextResponse.json({ error: "query too long" }, { status: 400 });
  }

  const url =
    "https://nominatim.openstreetmap.org/search?" +
    new URLSearchParams({
      q: q.trim(),
      format: "json",
      limit: "1",
      countrycodes: "us",
      addressdetails: "0",
    }).toString();

  let res: Response;
  try {
    res = await fetch(url, {
      headers: {
        "User-Agent": "OralCheck/1.0 (+https://oralcheck.org)",
        "Accept-Language": "en",
      },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ error: "geocode unavailable" }, { status: 502 });
  }

  if (!res.ok) {
    return NextResponse.json({ error: `geocode ${res.status}` }, { status: 502 });
  }

  const data = (await res.json()) as NominatimResult[];
  const first = data[0];
  if (!first) {
    return NextResponse.json({ error: "no results" }, { status: 404 });
  }

  return NextResponse.json({
    address: first.display_name,
    lat: parseFloat(first.lat),
    lng: parseFloat(first.lon),
    configured: true,
  });
}
