import {
  classify,
  haversineMiles,
  typeLabel,
  isPatientCare,
  DENTAL_RE,
  type Clinic,
} from "@/lib/clinics";

/**
 * Google Places API (New) lookup for the Find Care map.
 *
 * This is the primary source; Overpass/OSM is the fallback. The reason to pay
 * for Google at all is coverage and contact detail: OSM has patchy coverage of
 * US private dental practices and leaves phone/website/hours empty on most of
 * the ones it does have, and this page exists to actually get someone to an
 * appointment.
 */

const BASE = "https://places.googleapis.com/v1";
const TIMEOUT_MS = 8_000;

// The response field mask is what determines which SKU a call bills against.
// nationalPhoneNumber / websiteUri / rating / currentOpeningHours are
// Enterprise-tier fields, which carry a smaller monthly free allowance than the
// Pro tier. They are also the entire reason for using Google here, so the trade
// is deliberate. Budget shape: one call for the "dental" scope and three for
// "specialty", with results cached for 24h in the route.
const FIELD_MASK = [
  "places.id",
  "places.displayName",
  "places.formattedAddress",
  "places.location",
  "places.types",
  "places.nationalPhoneNumber",
  "places.websiteUri",
  "places.rating",
  "places.userRatingCount",
  "places.currentOpeningHours.openNow",
].join(",");

type GooglePlace = {
  id: string;
  displayName?: { text?: string };
  formattedAddress?: string;
  location?: { latitude: number; longitude: number };
  types?: string[];
  nationalPhoneNumber?: string;
  websiteUri?: string;
  rating?: number;
  userRatingCount?: number;
  currentOpeningHours?: { openNow?: boolean };
};

type PlacesResponse = { places?: GooglePlace[]; error?: { message?: string } };

export function googleConfigured(): boolean {
  return Boolean(process.env.GOOGLE_PLACES_API_KEY);
}

async function callPlaces(path: string, body: unknown): Promise<GooglePlace[]> {
  const key = process.env.GOOGLE_PLACES_API_KEY;
  if (!key) throw new Error("GOOGLE_PLACES_API_KEY is not set");

  const res = await fetch(`${BASE}/${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Goog-Api-Key": key,
      "X-Goog-FieldMask": FIELD_MASK,
    },
    body: JSON.stringify(body),
    cache: "no-store",
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });

  const data = (await res.json().catch(() => ({}))) as PlacesResponse;
  if (!res.ok) {
    // A quota cap returns 429; a disabled key or billing problem returns 403.
    // Both need to throw so the caller falls back to Overpass rather than
    // rendering an empty map.
    throw new Error(
      `Places ${res.status}: ${data.error?.message ?? "unknown error"}`,
    );
  }
  return data.places ?? [];
}

const ACADEMIC_TYPES = ["university", "school", "primary_school", "secondary_school"];

function toClinic(p: GooglePlace, from: { lat: number; lng: number }): Clinic | null {
  const name = p.displayName?.text;
  const lat = p.location?.latitude;
  const lng = p.location?.longitude;
  if (!name || lat === undefined || lng === undefined) return null;
  if (!isPatientCare(name)) return null;

  const types = p.types ?? [];
  let type = classify(name, types);
  // Mirrors the OSM path: an academic place whose name is actually dental is a
  // dental school even when the name reads like a clinic.
  if (types.some((t) => ACADEMIC_TYPES.includes(t)) && DENTAL_RE.test(name.toLowerCase())) {
    type = "dental-school";
  }

  return {
    id: `g-${p.id}`,
    name,
    address: p.formattedAddress ?? "",
    lat,
    lng,
    distanceMi: haversineMiles(from, { lat, lng }),
    type,
    typeLabel: typeLabel(type),
    phone: p.nationalPhoneNumber,
    website: p.websiteUri,
    rating: p.rating,
    totalRatings: p.userRatingCount,
    openNow: p.currentOpeningHours?.openNow,
  };
}

// Text queries for the categories Google has no place-type for. Nearby Search
// can only filter by its own type taxonomy, which has "dentist" but nothing for
// community health centres, free clinics, or dental schools.
const SPECIALTY_QUERIES = [
  "community health center",
  "free dental clinic",
  "dental school",
];

export async function searchGooglePlaces(
  lat: number,
  lng: number,
  radiusMeters: number,
  scope: "dental" | "specialty" | "all",
): Promise<Clinic[]> {
  // Google caps the circle at 50km.
  const radius = Math.min(radiusMeters, 50_000);
  const center = { latitude: lat, longitude: lng };
  const calls: Promise<GooglePlace[]>[] = [];

  if (scope === "dental" || scope === "all") {
    calls.push(
      callPlaces("places:searchNearby", {
        includedTypes: ["dentist"],
        maxResultCount: 20,
        locationRestriction: { circle: { center, radius } },
        rankPreference: "DISTANCE",
      }),
    );
  }

  if (scope === "specialty" || scope === "all") {
    for (const textQuery of SPECIALTY_QUERIES) {
      calls.push(
        callPlaces("places:searchText", {
          textQuery,
          maxResultCount: 20,
          locationBias: { circle: { center, radius } },
        }),
      );
    }
  }

  // One category failing shouldn't lose the others, but if every call fails the
  // caller needs to know so it can fall back to Overpass.
  const settled = await Promise.allSettled(calls);
  const ok = settled.filter((s) => s.status === "fulfilled");
  if (ok.length === 0) {
    const first = settled[0];
    throw new Error(
      first && first.status === "rejected"
        ? String(first.reason?.message ?? first.reason)
        : "all Places calls failed",
    );
  }
  for (const s of settled) {
    if (s.status === "rejected") {
      console.warn("[googlePlaces] call failed:", s.reason?.message ?? s.reason);
    }
  }

  const from = { lat, lng };
  const radiusMi = radius / 1609.34;
  const seen = new Set<string>();

  return ok
    .flatMap((s) => s.value)
    .map((p) => toClinic(p, from))
    .filter((c): c is Clinic => {
      if (!c) return false;
      // searchText biases toward the circle rather than restricting to it, so
      // it happily returns a clinic three states away when the area is sparse.
      if ((c.distanceMi ?? 0) > radiusMi) return false;
      if (seen.has(c.id)) return false;
      seen.add(c.id);
      return true;
    })
    .sort((a, b) => (a.distanceMi ?? 0) - (b.distanceMi ?? 0));
}
