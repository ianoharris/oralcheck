import { NextResponse } from "next/server";
import {
  classify,
  haversineMiles,
  typeLabel,
  DENTAL_RE,
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
type OverpassResponse = { elements?: OverpassElement[]; remark?: string };

// Public Overpass mirrors, tried in order. The main instance rate-limits (429)
// and 504s under load, so a fallback keeps the map working.
const OVERPASS_MIRRORS = [
  "https://overpass-api.de/api/interpreter",
  "https://overpass.kumi.systems/api/interpreter",
  "https://overpass.osm.ch/api/interpreter",
];

// Name patterns that map onto the UI's filter buttons. Overpass can't classify
// these for us: OSM has no "community health centre" tag, so we match on name.
const COMMUNITY_PAT =
  "community health|health cent|health clinic|neighborhood health|family health|federally qualified|FQHC|public health";
const FREE_PAT = "free clinic|free dental|charitable|volunteers in medicine|mission of mercy";
// Word-safe: a bare "dent" matches "inDEPENdent" and pulled whole school
// districts into the dental-school filter.
const SCHOOL_PAT = "dental|dentist|dentistry|orthodont|oral health|maxillofacial";

function boundingBox(lat: number, lng: number, meters: number): string {
  const dLat = meters / 111_320;
  const dLng = meters / (111_320 * Math.max(0.1, Math.cos((lat * Math.PI) / 180)));
  return `(${(lat - dLat).toFixed(5)},${(lng - dLng).toFixed(5)},${(lat + dLat).toFixed(5)},${(lng + dLng).toFixed(5)})`;
}

function buildQuery(lat: number, lng: number, radiusMeters: number): string {
  // Deliberately a BOUNDING BOX, not (around:). Overpass can't use its spatial
  // index for `around` combined with a name regex — measured at 70s+ / timeout
  // versus ~4s for the identical bbox query. We trim to the true circular
  // radius in JS afterwards using haversine, so results are identical.
  const b = boundingBox(lat, lng, radiusMeters);
  const lines = [
    // Dental practices: the always-present backbone of the results.
    `nwr["amenity"="dentist"]${b};`,
    `nwr["healthcare"="dentist"]${b};`,
  ];
  // Community health centres / FQHCs. Anchored on an exact (indexed) tag value
  // then narrowed by name, so we don't pull in unrelated OB/GYN or diabetes clinics.
  for (const am of ["clinic", "doctors", "hospital"]) {
    lines.push(`nwr["amenity"="${am}"]["name"~"${COMMUNITY_PAT}",i]${b};`);
  }
  for (const hc of ["centre", "clinic", "hospital"]) {
    lines.push(`nwr["healthcare"="${hc}"]["name"~"${COMMUNITY_PAT}",i]${b};`);
  }
  // Free / charitable clinics.
  for (const am of ["clinic", "doctors", "social_facility"]) {
    lines.push(`nwr["amenity"="${am}"]["name"~"${FREE_PAT}",i]${b};`);
  }
  // Dental schools: academic amenities whose name mentions dentistry. Many US
  // dental schools carry only building=university with no amenity tag at all
  // (NYU College of Dentistry, Columbia's College of Dental Medicine), so both
  // tagging styles have to be queried or the dental-school filter stays empty.
  for (const am of ["university", "college", "school"]) {
    lines.push(`nwr["amenity"="${am}"]["name"~"${SCHOOL_PAT}",i]${b};`);
    lines.push(`nwr["building"="${am}"]["name"~"${SCHOOL_PAT}",i]${b};`);
  }
  return `[out:json][timeout:30];\n(\n  ${lines.join("\n  ")}\n);\nout center tags 200;`;
}

/**
 * Keep the nearest few of each scarce category before filling the rest with
 * dental practices. A flat nearest-40 slice let dense city dentists push the
 * single community health centre off the end, which made those filters look
 * broken even when the data was there.
 */
function selectBalanced(clinics: Clinic[], limit: number): Clinic[] {
  const QUOTA: Partial<Record<Clinic["type"], number>> = {
    "community-health": 12,
    "dental-school": 6,
    free: 8,
  };
  const picked: Clinic[] = [];
  const taken = new Set<string>();
  for (const [type, quota] of Object.entries(QUOTA)) {
    for (const c of clinics.filter((x) => x.type === type).slice(0, quota)) {
      picked.push(c);
      taken.add(c.id);
    }
  }
  for (const c of clinics) {
    if (picked.length >= limit) break;
    if (!taken.has(c.id)) {
      picked.push(c);
      taken.add(c.id);
    }
  }
  return picked.sort((a, b) => (a.distanceMi ?? 0) - (b.distanceMi ?? 0));
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
  let type = classify(name, osmTypes);
  // An OSM-tagged academic institution is a dental school even when its name
  // reads like a clinic ("Eastman Institute for Oral Health"), but only if the
  // name is actually dental — otherwise ordinary schools slip through.
  const ACADEMIC_TAGS = ["university", "college", "school"];
  const isAcademic =
    ACADEMIC_TAGS.includes(t.amenity ?? "") || ACADEMIC_TAGS.includes(t.building ?? "");
  if (isAcademic && DENTAL_RE.test(name.toLowerCase())) {
    type = "dental-school";
  }

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
  const query = buildQuery(lat, lng, radiusMeters);
  const radiusMi = radiusMeters / 1609.34;
  let lastErr: unknown;

  for (const url of OVERPASS_MIRRORS) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          // Overpass returns 406 without a descriptive User-Agent.
          "User-Agent": "OralCheck/1.0 (+https://oralcheck.org)",
          Accept: "application/json",
        },
        body: new URLSearchParams({ data: query }).toString(),
        cache: "no-store",
        signal: AbortSignal.timeout(30_000),
      });
      if (!res.ok) throw new Error(`Overpass ${res.status}`);
      const data = (await res.json()) as OverpassResponse;
      // A timed-out query still returns 200 with a `remark`; treat that as failure
      // so we fall through to the next mirror instead of showing an empty map.
      if (data.remark && !(data.elements ?? []).length) {
        throw new Error(`Overpass remark: ${data.remark}`);
      }

      const seen = new Set<string>();
      const clinics = (data.elements ?? [])
        .map((el) => toClinic(el, { lat, lng }))
        .filter((c): c is Clinic => {
          if (!c) return false;
          // Trim the bbox down to the true circular radius.
          if ((c.distanceMi ?? 0) > radiusMi) return false;
          if (seen.has(c.id)) return false;
          seen.add(c.id);
          return true;
        })
        .sort((a, b) => (a.distanceMi ?? 0) - (b.distanceMi ?? 0));

      return selectBalanced(clinics, 60);
    } catch (e) {
      lastErr = e;
      console.warn(`[api/clinics] mirror failed (${url}):`, e);
    }
  }
  throw lastErr ?? new Error("All Overpass mirrors failed");
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
