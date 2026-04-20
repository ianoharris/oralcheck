"use client";

import { useMemo } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
  useMap,
} from "@vis.gl/react-google-maps";
import { useEffect } from "react";
import type { Clinic } from "@/lib/clinics";

const MAP_ID = "oralcheck-map";

function FitToBounds({
  center,
  clinics,
}: {
  center: { lat: number; lng: number };
  clinics: Clinic[];
}) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    if (clinics.length === 0) {
      map.panTo(center);
      return;
    }
    const bounds = new google.maps.LatLngBounds();
    bounds.extend(center);
    for (const c of clinics) bounds.extend({ lat: c.lat, lng: c.lng });
    map.fitBounds(bounds, 60);
  }, [map, center, clinics]);

  return null;
}

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

export default function ClinicMap({
  apiKey,
  clinics,
  center,
  selectedId,
  onSelect,
}: {
  apiKey: string;
  clinics: Clinic[];
  center: { lat: number; lng: number };
  selectedId?: string;
  onSelect?: (id: string) => void;
}) {
  const defaultCenter = useMemo(() => center, [center]);

  return (
    <APIProvider apiKey={apiKey}>
      <Map
        mapId={MAP_ID}
        defaultCenter={defaultCenter}
        defaultZoom={12}
        gestureHandling="greedy"
        disableDefaultUI={false}
        className="w-full h-full rounded-2xl"
      >
        <AdvancedMarker position={center}>
          <div className="w-4 h-4 rounded-full bg-white border-4 border-brand shadow-md" />
        </AdvancedMarker>

        {clinics.map((c) => {
          const colors = pinColor(c.type);
          const selected = c.id === selectedId;
          return (
            <AdvancedMarker
              key={c.id}
              position={{ lat: c.lat, lng: c.lng }}
              onClick={() => onSelect?.(c.id)}
            >
              <Pin
                background={colors.bg}
                borderColor={colors.border}
                glyphColor="#ffffff"
                scale={selected ? 1.4 : 1}
              />
            </AdvancedMarker>
          );
        })}

        <FitToBounds center={center} clinics={clinics} />
      </Map>
    </APIProvider>
  );
}
