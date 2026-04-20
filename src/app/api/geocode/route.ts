import { NextResponse } from "next/server";

type GeocodeResponse = {
  results?: {
    formatted_address: string;
    geometry: { location: { lat: number; lng: number } };
  }[];
  status: string;
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get("q");

  if (!q || !q.trim()) {
    return NextResponse.json(
      { error: "q query parameter is required" },
      { status: 400 },
    );
  }

  const key =
    process.env.GOOGLE_PLACES_API_KEY ??
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  if (!key) {
    return NextResponse.json(
      { error: "geocoding not configured", configured: false },
      { status: 503 },
    );
  }

  const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(q)}&key=${key}`;
  const res = await fetch(url, { cache: "no-store" });

  if (!res.ok) {
    return NextResponse.json(
      { error: `geocode ${res.status}` },
      { status: 502 },
    );
  }

  const data = (await res.json()) as GeocodeResponse;
  const first = data.results?.[0];
  if (!first) {
    return NextResponse.json(
      { error: "no results", status: data.status },
      { status: 404 },
    );
  }

  return NextResponse.json({
    address: first.formatted_address,
    lat: first.geometry.location.lat,
    lng: first.geometry.location.lng,
    configured: true,
  });
}
