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
  source: "openstreetmap" | "google-places" | "mock";
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

const FREE_RE = /free clinic|free dental|charitable|volunteers in medicine|mission of mercy/;
const COMMUNITY_RE =
  /community health|health cent|health clinic|neighborhood health|family health|federally qualified|fqhc|public health/;
// Never use a bare /dent/ or /oral/ here: "dent" is inside "indepenDENT"
// (which tagged "Houston Independent School District" as a dental school) and
// "oral" is inside "corpORAL"/"tempORAL".
export const DENTAL_RE = /dental|dentist|dentistry|orthodont|periodont|endodont|\boral\b|maxillofacial/;

// Requires an unambiguous academic-dental phrase. A loose "academic word AND
// dental word" test misfired on private practices like "University Square Dental".
// Genuinely institution-tagged places are caught by the OSM amenity override
// in the clinics route instead.
const DENTAL_SCHOOL_RE =
  /school of dent|dental school|college of dent|dental college|school of dental|dental medicine|faculty of dent|dental hygiene program/;

export function classify(name: string, types: string[] = []): Clinic["type"] {
  const n = name.toLowerCase();
  if (FREE_RE.test(n)) return "free";
  if (DENTAL_SCHOOL_RE.test(n)) return "dental-school";
  if (COMMUNITY_RE.test(n)) return "community-health";
  if (types.includes("dentist") || DENTAL_RE.test(n)) return "dental";
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
