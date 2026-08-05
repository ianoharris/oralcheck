"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import type { Clinic, ClinicSearchResult } from "@/lib/clinics";
import ClinicMap from "@/components/ClinicMap";

type ClinicTypeFilter = "all" | "community-health" | "dental-school" | "free";

const DEFAULT_CENTER = { lat: 40.7527, lng: -73.9772 };

export default function FindCarePage() {
  const t = useTranslations("FindCarePage");
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
        setError(t("errorLoad"));
        console.error(e);
      } finally {
        setLoading(false);
      }
    },
    [t],
  );

  const useMyLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError(t("errorNoGeo"));
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        fetchClinics(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        setLoading(false);
        setError(t("errorLocationDenied"));
      },
      { timeout: 10_000 },
    );
  }, [fetchClinics, t]);

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
        if (!geo.ok) throw new Error(`geocode ${geo.status}`);
        const { lat, lng } = await geo.json();
        await fetchClinics(lat, lng);
      } catch {
        setError(t("errorNoAddress"));
        setLoading(false);
      }
    },
    [query, fetchClinics, t],
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

  const filters: { id: ClinicTypeFilter; label: string }[] = [
    { id: "all", label: t("filterAll") },
    { id: "community-health", label: t("filterCommunityHealth") },
    { id: "dental-school", label: t("filterDentalSchools") },
    { id: "free", label: t("filterFreeClinics") },
  ];

  return (
    <div className="max-w-6xl mx-auto px-5 py-10 sm:py-16">
      <div className="max-w-2xl mb-10">
        <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">
          {t("heading")}
        </h1>
        <p className="text-ink-soft text-lg leading-relaxed">
          {t("subheading")}
        </p>
      </div>

      {result && result.source === "mock" && (
        <div className="mb-6 p-4 rounded-2xl bg-warm-dim/60 border border-warm-dim text-sm text-ink-soft">
          <strong className="text-ink">{t("mockBannerBold")}</strong> {t("mockBannerRest")}
        </div>
      )}

      <form
        onSubmit={searchByQuery}
        className="bg-warm-dim rounded-2xl border border-warm-dim p-5 mb-6 flex flex-col sm:flex-row gap-3"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("searchPlaceholder")}
          className="flex-1 bg-warm px-5 py-3 rounded-xl border border-warm-dim focus:outline-none focus:ring-2 focus:ring-brand text-ink placeholder:text-ink-soft"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-brand hover:bg-brand-dark disabled:bg-warm-dim disabled:text-ink-soft text-white font-semibold px-6 py-3 rounded-xl transition-colors"
        >
          {loading ? t("searching") : t("search")}
        </button>
        <button
          type="button"
          onClick={useMyLocation}
          disabled={loading}
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-xl transition-colors border border-warm-dim"
        >
          {t("useMyLocation")}
        </button>
      </form>

      <div className="flex flex-wrap gap-2 mb-6">
        {filters.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`text-sm font-medium px-4 py-1.5 rounded-full transition-colors ${
              filter === f.id
                ? "bg-brand text-white"
                : "bg-warm-dim text-ink-soft border border-warm-dim hover:text-ink"
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
            <div className="text-sm text-ink-soft p-5 bg-warm-dim rounded-2xl border border-warm-dim">
              {t("noClinics")}
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
            <ClinicMap
              clinics={visible}
              center={center}
              selectedId={selectedId}
              onSelect={handleSelect}
            />
          </div>
        </div>
      </div>

      <div className="mt-12 p-6 rounded-2xl bg-warm-dim border border-warm-dim">
        <h2 className="font-serif text-2xl text-ink mb-2">
          {t("cantFindHeading")}
        </h2>
        <ul className="space-y-2 text-sm text-ink-soft leading-relaxed">
          <li>
            <strong className="text-ink">{t("hrsaLabel")}</strong>{" "}
            {t("hrsaBody")}{" "}
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
            <strong className="text-ink">{t("dentalSchoolsLabel")}</strong> {t("dentalSchoolsBody")}
          </li>
          <li>
            <strong className="text-ink">{t("lifelineLabel")}</strong>{" "}
            {t("lifelineBody")}
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
  const t = useTranslations("FindCarePage");
  const tType = useTranslations("ClinicType");
  return (
    <button
      id={`clinic-${clinic.id}`}
      onClick={onSelect}
      className={`w-full text-left bg-warm-dim rounded-2xl border p-5 transition-colors ${
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
          {tType(clinic.type)}
        </span>
        {clinic.isHrsa && (
          <span className="inline-block text-xs font-semibold text-low bg-low/10 px-2.5 py-0.5 rounded-full">
            {t("hrsaFunded")}
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
            {clinic.openNow ? t("openNow") : t("closed")}
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
              {t("website")}
            </a>
          )}
        </div>
      )}
      {clinic.rating !== undefined && (
        <div className="mt-2 text-xs text-ink-soft">
          ★ {clinic.rating.toFixed(1)}
          {clinic.totalRatings !== undefined && (
            <span> {t("reviews", { count: clinic.totalRatings })}</span>
          )}
        </div>
      )}
    </button>
  );
}
