import { NextResponse } from "next/server";
import {
  classify,
  haversineMiles,
  typeLabel,
  isPatientCare,
  DENTAL_RE,
  type Clinic,
  type ClinicSearchResult,
} from "@/lib/clinics";
import { checkRateLimit, getIp } from "@/lib/rateLimit";
import { searchGooglePlaces, googleConfigured } from "@/lib/googlePlaces";

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

// Public Overpass mirrors, raced against each other.
//
// Every entry here must carry PLANET-WIDE data. overpass.osm.ch was in this
// list and is Switzerland-only: it answered US queries in ~0.4s with zero
// results, won the race every time, and the empty result silently demoted the
// whole map to sample data. Verified before adding: each of these returns 100+
// dentists for a Manhattan bounding box.
const OVERPASS_MIRRORS = [
  "https://overpass-api.de/api/interpreter",
  "https://overpass.kumi.systems/api/interpreter",
  "https://overpass.private.coffee/api/interpreter",
];

// Two-phase lookup. The plain dentist clauses answer in ~8s, while the
// name-regex clauses that populate the community-health / free / dental-school
// filters cost another ~13s no matter how few of them there are (the cost is
// the scan, not the clause count). Fetching them separately lets the map paint
// real results at ~8s instead of showing nothing for ~21s.
export type Scope = "dental" | "specialty" | "all";

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

function buildQuery(lat: number, lng: number, radiusMeters: number, scope: Scope = "all"): string {
  // Deliberately a BOUNDING BOX, not (around:). Overpass can't use its spatial
  // index for `around` combined with a name regex — measured at 70s+ / timeout
  // versus ~4s for the identical bbox query. We trim to the true circular
  // radius in JS afterwards using haversine, so results are identical.
  const b = boundingBox(lat, lng, radiusMeters);
  const lines: string[] = [];

  if (scope === "dental" || scope === "all") {
    // Dental practices: the always-present backbone of the results, and the
    // only clauses cheap enough to answer quickly.
    lines.push(`nwr["amenity"="dentist"]${b};`);
    lines.push(`nwr["healthcare"="dentist"]${b};`);
  }

  if (scope === "specialty" || scope === "all") {
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
  if (!isPatientCare(name)) return null;
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

const MIRROR_TIMEOUT_MS = 15_000;

// Overpass is the slow part and OSM clinic data barely moves, so results are
// worth holding onto. Coordinates are rounded to ~1km before keying, which
// means panning slightly or re-searching the same town is an instant hit
// instead of another multi-second lookup.
const CACHE_TTL_MS = 24 * 60 * 60 * 1000;
const CACHE_MAX = 200;
type Source = ClinicSearchResult["source"];
type CacheEntry = { at: number; clinics: Clinic[]; source: Source };
const cache = new Map<string, CacheEntry>();

function cacheKey(lat: number, lng: number, radiusMi: number, scope: Scope): string {
  return `${scope}:${lat.toFixed(2)},${lng.toFixed(2)},${Math.round(radiusMi)}`;
}

function cacheGet(key: string): CacheEntry | null {
  const hit = cache.get(key);
  if (!hit) return null;
  if (Date.now() - hit.at > CACHE_TTL_MS) {
    cache.delete(key);
    return null;
  }
  // refresh recency for the LRU eviction below
  cache.delete(key);
  cache.set(key, hit);
  return hit;
}

function cacheSet(key: string, clinics: Clinic[], source: Source): void {
  cache.set(key, { at: Date.now(), clinics, source });
  while (cache.size > CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest === undefined) break;
    cache.delete(oldest);
  }
}

async function queryMirror(
  url: string,
  query: string,
  lat: number,
  lng: number,
  radiusMi: number,
): Promise<Clinic[]> {
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
    signal: AbortSignal.timeout(MIRROR_TIMEOUT_MS),
  });
  if (!res.ok) throw new Error(`Overpass ${res.status}`);
  const data = (await res.json()) as OverpassResponse;
  // A timed-out query still returns 200 with a `remark`; treat that as a failure
  // so this mirror loses the race rather than resolving with an empty map.
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

  // A mirror that lacks coverage for this area answers fast and empty. Treat
  // that as a loss so it can't beat a mirror that actually has the data; if
  // every mirror genuinely finds nothing, the caller still falls back.
  if (clinics.length === 0) throw new Error("no results from this mirror");

  return selectBalanced(clinics, 60);
}

async function searchOverpass(
  lat: number,
  lng: number,
  radiusMeters: number,
  scope: Scope,
): Promise<Clinic[]> {
  const query = buildQuery(lat, lng, radiusMeters, scope);
  const radiusMi = radiusMeters / 1609.34;

  // Race every mirror at once and take the first that answers. Trying them in
  // sequence meant a single overloaded instance cost its full timeout before
  // the next was attempted, which is how a lookup reached 40s. Public Overpass
  // load varies minute to minute, so whichever is healthy right now wins.
  try {
    return await Promise.any(
      OVERPASS_MIRRORS.map((url) =>
        queryMirror(url, query, lat, lng, radiusMi).catch((e) => {
          console.warn(`[api/clinics] mirror lost (${url}):`, e?.message ?? e);
          throw e;
        }),
      ),
    );
  } catch {
    throw new Error("All Overpass mirrors failed");
  }
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
  const scopeParam = searchParams.get("scope");
  const scope: Scope =
    scopeParam === "dental" || scopeParam === "specialty" ? scopeParam : "all";

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return NextResponse.json(
      { error: "lat and lng query parameters are required" },
      { status: 400 },
    );
  }

  // Served straight from cache when we've looked up this area recently. This is
  // also the main cost control on the Google side: a repeated search for the
  // same area costs nothing for 24h.
  const key = cacheKey(lat, lng, radiusMi, scope);
  const cached = cacheGet(key);
  if (cached) {
    return NextResponse.json(
      { clinics: cached.clinics, center: { lat, lng }, source: cached.source, configured: true } satisfies ClinicSearchResult,
      { headers: { "X-Cache": "HIT", "X-Source": cached.source, "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800" } },
    );
  }

  const radiusMeters = radiusMi * 1609.34;

  // Google first: better coverage of US dental practices, and it fills in the
  // phone / website / hours / rating that OSM almost always leaves blank.
  if (googleConfigured()) {
    try {
      const clinics = await searchGooglePlaces(lat, lng, radiusMeters, scope);
      if (clinics.length > 0) {
        cacheSet(key, clinics, "google");
        return NextResponse.json(
          { clinics, center: { lat, lng }, source: "google", configured: true } satisfies ClinicSearchResult,
          { headers: { "X-Cache": "MISS", "X-Source": "google", "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800" } },
        );
      }
      console.warn("[api/clinics] Google returned no results, falling back to Overpass");
    } catch (e) {
      // Quota caps (429) and billing/key problems (403) land here. Falling back
      // keeps the map working instead of turning a spend cap into an outage.
      console.warn("[api/clinics] Google lookup failed, falling back to Overpass:", e);
    }
  }

  try {
    const clinics = await searchOverpass(lat, lng, radiusMeters, scope);
    cacheSet(key, clinics, "openstreetmap");
    const result: ClinicSearchResult = {
      clinics,
      center: { lat, lng },
      source: "openstreetmap",
      configured: true,
    };
    return NextResponse.json(result, {
      headers: { "X-Cache": "MISS", "X-Source": "openstreetmap", "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800" },
    });
  } catch (e) {
    console.error("[api/clinics] Overpass lookup failed:", e);
    // Deliberately an error, not sample data. This page exists to send someone
    // to real care; a fabricated clinic listing is worse than telling them the
    // directory is temporarily unreachable.
    return NextResponse.json(
      { error: "upstream_unavailable" },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}
