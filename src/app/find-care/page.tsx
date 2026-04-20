"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Clinic, ClinicSearchResult } from "@/lib/clinics";
import ClinicMap from "@/components/ClinicMap";

type ClinicTypeFilter = "all" | "community-health" | "dental-school" | "free";

const DEFAULT_CENTER = { lat: 40.7527, lng: -73.9772 };

export default function FindCarePage() {
  const mapsKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? "";
  const hasMaps = Boolean(mapsKey);

  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ClinicTypeFilter>("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClinicSearchResult | null>(null);
  const [selectedId, setSelectedId] = useState<string | undefined>();
  const listRef = useRef<HTMLDivElement>(null);

  const fetchClinics = useCallback(
    async (lat: number, lng: number) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `/api/clinics?lat=${lat}&lng=${lng}&radius=10`,
        );
        if (!res.ok) throw new Error(`${res.status}`);
        const data: ClinicSearchResult = await res.json();
        setResult(data);
      } catch (e) {
        setError("We couldn't load clinics. Please try again.");
        console.error(e);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const useMyLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Your browser doesn't support location.");
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        fetchClinics(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        setLoading(false);
        setError("Location permission denied. Try searching by ZIP code.");
      },
      { timeout: 10_000 },
    );
  }, [fetchClinics]);

  const searchByQuery = useCallback(
    async (e?: React.FormEvent) => {
      e?.preventDefault();
      if (!query.trim()) return;
      setLoading(true);
      setError(null);
      try {
        const geo = await fetch(
          `/api/geocode?q=${encodeURIComponent(query)}`,
        );
        if (geo.status === 503) {
          setError(
            "Address search needs a Google Maps API key. Try 'Use my location' instead.",
          );
          setLoading(false);
          return;
        }
        if (!geo.ok) throw new Error(`geocode ${geo.status}`);
        const { lat, lng } = await geo.json();
        await fetchClinics(lat, lng);
      } catch {
        setError("We couldn't find that address. Try again.");
        setLoading(false);
      }
    },
    [query, fetchClinics],
  );

  // On first load, populate with default-center mock so there's something to see.
  useEffect(() => {
    fetchClinics(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng);
  }, [fetchClinics]);

  const clinics = result?.clinics ?? [];
  const visible =
    filter === "all" ? clinics : clinics.filter((c) => c.type === filter);
  const center = result?.center ?? DEFAULT_CENTER;

  const handleSelect = (id: string) => {
    setSelectedId(id);
    const el = document.getElementById(`clinic-${id}`);
    el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  return (
    <div className="max-w-6xl mx-auto px-5 py-10 sm:py-16">
      <div className="max-w-2xl mb-10">
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">
          Find affordable care
        </h1>
        <p className="text-ink-soft text-lg leading-relaxed">
          Community health centers, dental schools, and free clinics near you.
          Most offer oral cancer screenings as part of a routine visit.
        </p>
      </div>

      {result && !result.configured && (
        <div className="mb-6 p-4 rounded-2xl bg-warm-dim/60 border border-warm-dim text-sm text-ink-soft">
          <strong className="text-ink">Demo mode:</strong> showing sample
          clinics. Add a <code className="font-mono text-xs bg-warm px-1.5 py-0.5 rounded">GOOGLE_PLACES_API_KEY</code>{" "}
          in <code className="font-mono text-xs bg-warm px-1.5 py-0.5 rounded">.env.local</code>{" "}
          to see real providers near you.
        </div>
      )}

      <form
        onSubmit={searchByQuery}
        className="bg-white rounded-2xl border border-warm-dim p-5 mb-6 flex flex-col sm:flex-row gap-3"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter zip code or city"
          className="flex-1 bg-warm px-5 py-3 rounded-xl border border-warm-dim focus:outline-none focus:ring-2 focus:ring-brand text-ink placeholder:text-ink-soft"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-brand hover:bg-brand-dark disabled:bg-warm-dim disabled:text-ink-soft text-white font-semibold px-6 py-3 rounded-xl transition-colors"
        >
          {loading ? "Searching…" : "Search"}
        </button>
        <button
          type="button"
          onClick={useMyLocation}
          disabled={loading}
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-xl transition-colors border border-warm-dim"
        >
          Use my location
        </button>
      </form>

      <div className="flex flex-wrap gap-2 mb-6">
        {(
          [
            { id: "all", label: "All" },
            { id: "community-health", label: "Community health" },
            { id: "dental-school", label: "Dental schools" },
            { id: "free", label: "Free clinics" },
          ] as { id: ClinicTypeFilter; label: string }[]
        ).map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`text-sm font-medium px-4 py-1.5 rounded-full transition-colors ${
              filter === f.id
                ? "bg-brand text-white"
                : "bg-white text-ink-soft border border-warm-dim hover:text-ink"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-2xl bg-accent/10 border border-accent/30 text-sm text-ink">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div
          ref={listRef}
          className="lg:col-span-2 space-y-3 order-2 lg:order-1 lg:max-h-[600px] lg:overflow-y-auto lg:pr-2"
        >
          {visible.length === 0 && !loading && (
            <div className="text-sm text-ink-soft p-5 bg-white rounded-2xl border border-warm-dim">
              No clinics match this filter in your area.
            </div>
          )}
          {visible.map((c) => (
            <ClinicCard
              key={c.id}
              clinic={c}
              selected={c.id === selectedId}
              onSelect={() => setSelectedId(c.id)}
            />
          ))}
        </div>

        <div className="lg:col-span-3 order-1 lg:order-2">
          <div className="aspect-square lg:aspect-auto lg:h-[600px] rounded-2xl overflow-hidden border border-warm-dim bg-brand-soft relative">
            {hasMaps ? (
              <ClinicMap
                apiKey={mapsKey}
                clinics={visible}
                center={center}
                selectedId={selectedId}
                onSelect={handleSelect}
              />
            ) : (
              <MapPreviewFallback clinics={visible} />
            )}
          </div>
        </div>
      </div>

      <div className="mt-12 p-6 rounded-2xl bg-white border border-warm-dim">
        <h2 className="font-serif text-2xl text-ink mb-2">
          Can&apos;t find affordable care?
        </h2>
        <ul className="space-y-2 text-sm text-ink-soft leading-relaxed">
          <li>
            <strong className="text-ink">HRSA Find a Health Center:</strong>{" "}
            The US government maintains a directory of community health
            centers with sliding-scale dental services at{" "}
            <a
              href="https://findahealthcenter.hrsa.gov"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand hover:underline"
            >
              findahealthcenter.hrsa.gov
            </a>
            .
          </li>
          <li>
            <strong className="text-ink">Dental schools:</strong> Most US
            dental schools operate teaching clinics with significantly reduced
            fees.
          </li>
          <li>
            <strong className="text-ink">Dental Lifeline Network:</strong>{" "}
            Connects people with disabilities, elderly, and medically fragile
            patients to volunteer dentists.
          </li>
        </ul>
      </div>
    </div>
  );
}

function ClinicCard({
  clinic,
  selected,
  onSelect,
}: {
  clinic: Clinic;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      id={`clinic-${clinic.id}`}
      onClick={onSelect}
      className={`w-full text-left bg-white rounded-2xl border p-5 transition-colors ${
        selected ? "border-brand bg-brand-soft" : "border-warm-dim hover:border-brand/40"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-1">
        <h3 className="font-semibold text-ink">{clinic.name}</h3>
        {clinic.distanceMi !== undefined && (
          <span className="text-xs font-mono text-ink-soft shrink-0">
            {clinic.distanceMi.toFixed(1)} mi
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5 mb-2">
        <span className="inline-block text-xs font-semibold text-brand bg-brand-soft px-2.5 py-0.5 rounded-full">
          {clinic.typeLabel}
        </span>
        {clinic.isHrsa && (
          <span className="inline-block text-xs font-semibold text-low bg-low/10 px-2.5 py-0.5 rounded-full">
            HRSA-funded
          </span>
        )}
        {clinic.openNow !== undefined && (
          <span
            className={`inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full ${
              clinic.openNow
                ? "text-low bg-low/10"
                : "text-ink-soft bg-warm-dim"
            }`}
          >
            {clinic.openNow ? "Open now" : "Closed"}
          </span>
        )}
      </div>
      {clinic.address && (
        <div className="text-sm text-ink-soft">{clinic.address}</div>
      )}
      {(clinic.phone || clinic.website) && (
        <div className="mt-2 flex flex-wrap gap-3 text-sm">
          {clinic.phone && (
            <a
              href={`tel:${clinic.phone}`}
              onClick={(e) => e.stopPropagation()}
              className="text-brand hover:underline"
            >
              {clinic.phone}
            </a>
          )}
          {clinic.website && (
            <a
              href={clinic.website}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-brand hover:underline"
            >
              Website
            </a>
          )}
        </div>
      )}
      {clinic.rating !== undefined && (
        <div className="mt-2 text-xs text-ink-soft">
          ★ {clinic.rating.toFixed(1)}
          {clinic.totalRatings !== undefined && (
            <span> ({clinic.totalRatings} reviews)</span>
          )}
        </div>
      )}
    </button>
  );
}

function MapPreviewFallback({ clinics }: { clinics: Clinic[] }) {
  return (
    <div aria-hidden className="absolute inset-0">
      <svg
        className="absolute inset-0 w-full h-full opacity-30"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="var(--color-brand)"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {clinics.slice(0, 5).map((c, i) => {
        const positions = [
          { top: "20%", left: "25%" },
          { top: "45%", left: "60%" },
          { top: "35%", left: "40%" },
          { top: "65%", left: "30%" },
          { top: "55%", left: "75%" },
        ];
        const pos = positions[i % positions.length];
        return (
          <div
            key={c.id}
            className="absolute -translate-x-1/2 -translate-y-full"
            style={pos}
          >
            <div className="flex flex-col items-center">
              <div className="w-6 h-6 rounded-full bg-accent border-2 border-white shadow-md flex items-center justify-center text-white text-xs font-bold">
                {i + 1}
              </div>
              <div className="w-0.5 h-3 bg-accent" />
            </div>
          </div>
        );
      })}

      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur rounded-xl px-4 py-2 text-xs text-ink-soft">
        Add <code className="font-mono">NEXT_PUBLIC_GOOGLE_MAPS_API_KEY</code>{" "}
        to see the live map
      </div>
    </div>
  );
}
