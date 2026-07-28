import { NextResponse } from "next/server";
import {
  classify,
  haversineMiles,
  typeLabel,
  type Clinic,
  type ClinicSearchResult,
} from "@/lib/clinics";
import { mockClinics } from "@/lib/mockClinics";
import { checkRateLimit, getIp } from "@/lib/rateLimit";

// Free clinic search via the OpenStreetMap Overpass API (no key, no billing).
type OverpassElement = {
  type: "node" | "way" | "relation";
  id: number;
  lat?: number;
  lon?: number;
  center?: { lat: number; lon: number };
  tags?: Record<string, string>;
};
type OverpassResponse = { elements?: OverpassElement[] };

const OVERPASS_URL = "https://overpass-api.de/api/interpreter";

function buildQuery(lat: number, lng: number, radiusMeters: number): string {
  const r = Math.round(radiusMeters);
  const around = `(around:${r},${lat},${lng})`;
  // Dental / oral-health facilities only. Generic amenity=clinic/doctors pull in
  // unrelated places (OB/GYN, diabetes centres), so we stick to dentists and
  // anything tagged with a dental or oral speciality.
  return `[out:json][timeout:25];
(
  nwr["amenity"="dentist"]${around};
  nwr["healthcare"="dentist"]${around};
  nwr["healthcare:speciality"~"dent|oral|maxillofacial",i]${around};
);
out center tags 60;`;
}

function addressFromTags(t: Record<string, string>): string {
  const line1 = [t["addr:housenumber"], t["addr:street"]].filter(Boolean).join(" ");
  const line2 = [t["addr:city"], t["addr:state"], t["addr:postcode"]]
    .filter(Boolean)
    .join(", ")
    .replace(", " + (t["addr:postcode"] ?? ""), " " + (t["addr:postcode"] ?? ""));
  return [line1, line2].filter(Boolean).join(", ");
}

function toClinic(el: OverpassElement, from: { lat: number; lng: number }): Clinic | null {
  const t = el.tags ?? {};
  const name = t.name || t["operator"] || "";
  if (!name) return null;
  const lat = el.lat ?? el.center?.lat;
  const lng = el.lon ?? el.center?.lon;
  if (lat === undefined || lng === undefined) return null;

  // Give classify() the OSM signal so dentist offices are labelled correctly.
  const osmTypes: string[] = [];
  if (t.amenity === "dentist" || t.healthcare === "dentist") osmTypes.push("dentist");
  const type = classify(name, osmTypes);

  return {
    id: `osm-${el.type}-${el.id}`,
    name,
    address: addressFromTags(t),
    lat,
    lng,
    distanceMi: haversineMiles(from, { lat, lng }),
    type,
    typeLabel: typeLabel(type),
    phone: t.phone || t["contact:phone"] || undefined,
    website: t.website || t["contact:website"] || undefined,
  };
}

async function searchOverpass(
  lat: number,
  lng: number,
  radiusMeters: number,
): Promise<Clinic[]> {
  const res = await fetch(OVERPASS_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      // Overpass returns 406 without a descriptive User-Agent.
      "User-Agent": "OralCheck/1.0 (+https://oralcheck.org)",
      Accept: "application/json",
    },
    body: new URLSearchParams({ data: buildQuery(lat, lng, radiusMeters) }).toString(),
    cache: "no-store",
    signal: AbortSignal.timeout(25_000),
  });
  if (!res.ok) throw new Error(`Overpass ${res.status}`);
  const data = (await res.json()) as OverpassResponse;

  const seen = new Set<string>();
  return (data.elements ?? [])
    .map((el) => toClinic(el, { lat, lng }))
    .filter((c): c is Clinic => {
      if (!c) return false;
      if (seen.has(c.id)) return false;
      seen.add(c.id);
      return true;
    })
    .sort((a, b) => (a.distanceMi ?? 0) - (b.distanceMi ?? 0))
    .slice(0, 40);
}

export async function GET(request: Request) {
  const { allowed, resetMs } = checkRateLimit(getIp(request), 10);
  if (!allowed) {
    return NextResponse.json(
      { error: "rate_limited" },
      {
        status: 429,
        headers: {
          "Retry-After": String(Math.ceil(resetMs / 1000)),
          "X-RateLimit-Limit": "10",
          "X-RateLimit-Remaining": "0",
        },
      },
    );
  }

  const { searchParams } = new URL(request.url);
  const lat = parseFloat(searchParams.get("lat") ?? "");
  const lng = parseFloat(searchParams.get("lng") ?? "");
  const radiusMi = parseFloat(searchParams.get("radius") ?? "10");

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return NextResponse.json(
      { error: "lat and lng query parameters are required" },
      { status: 400 },
    );
  }

  try {
    const clinics = await searchOverpass(lat, lng, radiusMi * 1609.34);
    // Overpass coverage is sparse in some areas; fall back to samples if empty.
    if (clinics.length === 0) {
      const result: ClinicSearchResult = {
        clinics: mockClinics,
        center: { lat, lng },
        source: "mock",
        configured: true,
      };
      return NextResponse.json(result);
    }
    const result: ClinicSearchResult = {
      clinics,
      center: { lat, lng },
      source: "openstreetmap",
      configured: true,
    };
    return NextResponse.json(result);
  } catch (e) {
    console.error("[api/clinics] Overpass lookup failed:", e);
    const result: ClinicSearchResult = {
      clinics: mockClinics,
      center: { lat, lng },
      source: "mock",
      configured: true,
    };
    return NextResponse.json(result, { status: 200 });
  }
}
