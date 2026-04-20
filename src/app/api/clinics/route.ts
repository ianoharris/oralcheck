import { NextResponse } from "next/server";
import {
  classify,
  haversineMiles,
  typeLabel,
  type Clinic,
  type ClinicSearchResult,
} from "@/lib/clinics";
import { mockClinics } from "@/lib/mockClinics";

type PlacesNearbyResponse = {
  places?: {
    id: string;
    displayName?: { text: string };
    formattedAddress?: string;
    location?: { latitude: number; longitude: number };
    rating?: number;
    userRatingCount?: number;
    types?: string[];
    nationalPhoneNumber?: string;
    websiteUri?: string;
    currentOpeningHours?: { openNow?: boolean };
  }[];
};

const FIELD_MASK = [
  "places.id",
  "places.displayName",
  "places.formattedAddress",
  "places.location",
  "places.rating",
  "places.userRatingCount",
  "places.types",
  "places.nationalPhoneNumber",
  "places.websiteUri",
  "places.currentOpeningHours.openNow",
].join(",");

async function nearbySearch(
  key: string,
  lat: number,
  lng: number,
  radiusMeters: number,
  includedTypes: string[],
): Promise<PlacesNearbyResponse["places"]> {
  const res = await fetch(
    "https://places.googleapis.com/v1/places:searchNearby",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELD_MASK,
      },
      body: JSON.stringify({
        includedTypes,
        maxResultCount: 20,
        locationRestriction: {
          circle: {
            center: { latitude: lat, longitude: lng },
            radius: radiusMeters,
          },
        },
      }),
      cache: "no-store",
    },
  );

  if (!res.ok) {
    throw new Error(`Places API ${res.status}: ${await res.text()}`);
  }

  const data = (await res.json()) as PlacesNearbyResponse;
  return data.places ?? [];
}

async function textSearch(
  key: string,
  query: string,
  lat: number,
  lng: number,
  radiusMeters: number,
): Promise<PlacesNearbyResponse["places"]> {
  const res = await fetch(
    "https://places.googleapis.com/v1/places:searchText",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELD_MASK,
      },
      body: JSON.stringify({
        textQuery: query,
        maxResultCount: 10,
        locationBias: {
          circle: {
            center: { latitude: lat, longitude: lng },
            radius: radiusMeters,
          },
        },
      }),
      cache: "no-store",
    },
  );

  if (!res.ok) return [];
  const data = (await res.json()) as PlacesNearbyResponse;
  return data.places ?? [];
}

async function searchPlaces(
  key: string,
  lat: number,
  lng: number,
  radiusMeters: number,
): Promise<Clinic[]> {
  // Run searches in parallel: dentists + text searches for affordable care types
  const [dentistPlaces, communityPlaces, freePlaces] = await Promise.all([
    nearbySearch(key, lat, lng, radiusMeters, ["dentist"]),
    textSearch(key, "community health center dental", lat, lng, radiusMeters).catch(() => []),
    textSearch(key, "free dental clinic FQHC federally qualified health center", lat, lng, radiusMeters).catch(() => []),
  ]);

  // Merge and deduplicate by place id
  const seen = new Set<string>();
  const merged = [
    ...(dentistPlaces ?? []),
    ...(communityPlaces ?? []),
    ...(freePlaces ?? []),
  ].filter((p) => {
    if (!p.location || !p.displayName?.text) return false;
    if (seen.has(p.id)) return false;
    seen.add(p.id);
    return true;
  });

  return merged
    .map((p) => {
      const name = p.displayName!.text;
      const type = classify(name, p.types);
      const clinic: Clinic = {
        id: p.id,
        name,
        address: p.formattedAddress ?? "",
        lat: p.location!.latitude,
        lng: p.location!.longitude,
        distanceMi: haversineMiles(
          { lat, lng },
          { lat: p.location!.latitude, lng: p.location!.longitude },
        ),
        rating: p.rating,
        totalRatings: p.userRatingCount,
        type,
        typeLabel: typeLabel(type),
        phone: p.nationalPhoneNumber,
        website: p.websiteUri,
        openNow: p.currentOpeningHours?.openNow,
      };
      return clinic;
    })
    .sort((a, b) => (a.distanceMi ?? 0) - (b.distanceMi ?? 0));
}

export async function GET(request: Request) {
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

  const key = process.env.GOOGLE_PLACES_API_KEY;

  if (!key) {
    const result: ClinicSearchResult = {
      clinics: mockClinics,
      center: { lat, lng },
      source: "mock",
      configured: false,
    };
    return NextResponse.json(result);
  }

  try {
    const clinics = await searchPlaces(key, lat, lng, radiusMi * 1609.34);
    const result: ClinicSearchResult = {
      clinics,
      center: { lat, lng },
      source: "google-places",
      configured: true,
    };
    return NextResponse.json(result);
  } catch (e) {
    console.error("[api/clinics] Places lookup failed:", e);
    const result: ClinicSearchResult = {
      clinics: mockClinics,
      center: { lat, lng },
      source: "mock",
      configured: true,
    };
    return NextResponse.json(result, { status: 200 });
  }
}
