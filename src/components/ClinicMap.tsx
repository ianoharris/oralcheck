"use client";

import { useEffect, useRef } from "react";
import "leaflet/dist/leaflet.css";
import type * as LeafletNS from "leaflet";
import type { Clinic } from "@/lib/clinics";

function pinColor(type: Clinic["type"]): { bg: string; border: string } {
  switch (type) {
    case "community-health":
      return { bg: "#0d7377", border: "#095458" };
    case "dental-school":
      return { bg: "#7ba882", border: "#5e8866" };
    case "free":
      return { bg: "#e8634a", border: "#c84d35" };
    default:
      return { bg: "#6b6b6b", border: "#2d2d2d" };
  }
}

function pinHtml(bg: string, border: string, size: number): string {
  return `<div style="width:${size}px;height:${size}px;background:${bg};border:2px solid ${border};border-radius:50% 50% 50% 0;transform:rotate(-45deg);box-shadow:0 2px 4px rgba(0,0,0,.35)"></div>`;
}

const CENTER_HTML =
  '<div style="width:14px;height:14px;background:#fff;border:4px solid #0d7377;border-radius:50%;box-shadow:0 2px 4px rgba(0,0,0,.4)"></div>';

export default function ClinicMap({
  clinics,
  center,
  selectedId,
  onSelect,
}: {
  clinics: Clinic[];
  center: { lat: number; lng: number };
  selectedId?: string;
  onSelect?: (id: string) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletNS.Map | null>(null);
  const layerRef = useRef<LeafletNS.LayerGroup | null>(null);
  const LRef = useRef<typeof LeafletNS | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  // Initialise the map once (Leaflet is imported dynamically so it never runs
  // during SSR). OpenStreetMap tiles are free and need no API key.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const L = await import("leaflet");
      if (cancelled || !containerRef.current || mapRef.current) return;
      const map = L.map(containerRef.current, {
        center: [center.lat, center.lng],
        zoom: 12,
        scrollWheelZoom: true,
      });
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(map);
      LRef.current = L;
      layerRef.current = L.layerGroup().addTo(map);
      mapRef.current = map;
      setTimeout(() => map.invalidateSize(), 0);
      renderMarkers();
    })();
    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
      layerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function renderMarkers() {
    const L = LRef.current;
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!L || !map || !layer) return;
    layer.clearLayers();

    const bounds = L.latLngBounds([]);
    L.marker([center.lat, center.lng], {
      icon: L.divIcon({ className: "", html: CENTER_HTML, iconSize: [14, 14], iconAnchor: [7, 7] }),
      interactive: false,
      keyboard: false,
    }).addTo(layer);
    bounds.extend([center.lat, center.lng]);

    for (const c of clinics) {
      const { bg, border } = pinColor(c.type);
      const size = c.id === selectedId ? 30 : 22;
      const marker = L.marker([c.lat, c.lng], {
        icon: L.divIcon({
          className: "",
          html: pinHtml(bg, border, size),
          iconSize: [size, size],
          iconAnchor: [size / 2, size],
        }),
        title: c.name,
      }).addTo(layer);
      marker.on("click", () => onSelectRef.current?.(c.id));
      bounds.extend([c.lat, c.lng]);
    }

    if (clinics.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    } else {
      map.setView([center.lat, center.lng], 12);
    }
  }

  // Redraw markers whenever the data, centre, or selection changes.
  useEffect(() => {
    renderMarkers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clinics, center.lat, center.lng, selectedId]);

  return <div ref={containerRef} className="w-full h-full rounded-2xl" />;
}
