export type Clinic = {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  distanceMi?: number;
  rating?: number;
  totalRatings?: number;
  type: "dental" | "community-health" | "dental-school" | "free" | "other";
  typeLabel: string;
  isHrsa?: boolean;
  phone?: string;
  website?: string;
  openNow?: boolean;
};

export type ClinicSearchResult = {
  clinics: Clinic[];
  center: { lat: number; lng: number };
  source: "google-places" | "mock";
  configured: boolean;
};

export function haversineMiles(
  a: { lat: number; lng: number },
  b: { lat: number; lng: number },
): number {
  const R = 3958.8;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.sin(dLng / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return 2 * R * Math.asin(Math.sqrt(h));
}

export function classify(name: string, types: string[] = []): Clinic["type"] {
  const n = name.toLowerCase();
  if (n.includes("free clinic") || n.includes("free dental")) return "free";
  if (
    n.includes("community health") ||
    n.includes("health center") ||
    n.includes("fqhc") ||
    n.includes("public health")
  )
    return "community-health";
  if (
    n.includes("school of dent") ||
    n.includes("dental school") ||
    n.includes("college of dent") ||
    (n.includes("university") && types.includes("dentist"))
  )
    return "dental-school";
  if (types.includes("dentist") || n.includes("dent")) return "dental";
  return "other";
}

export function typeLabel(type: Clinic["type"]): string {
  switch (type) {
    case "community-health":
      return "Community health";
    case "dental-school":
      return "Dental school";
    case "free":
      return "Free clinic";
    case "dental":
      return "Dental practice";
    default:
      return "Clinic";
  }
}
