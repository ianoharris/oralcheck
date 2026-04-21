import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "OralCheck — 2 Minutes Could Save Your Life";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#faf9f6",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "space-between",
          padding: "72px 80px",
          fontFamily: "Georgia, serif",
        }}
      >
        {/* Top: wordmark + pill */}
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <div
            style={{
              width: "18px",
              height: "18px",
              borderRadius: "50%",
              background: "#e8634a",
            }}
          />
          <span style={{ fontSize: 36, color: "#0d7377", fontWeight: 700 }}>
            OralCheck
          </span>
          <div
            style={{
              background: "#0d7377",
              color: "#fff",
              fontSize: 16,
              fontWeight: 600,
              padding: "6px 16px",
              borderRadius: "999px",
              marginLeft: 8,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            Free · Private
          </div>
        </div>

        {/* Center: headline */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div
            style={{
              fontSize: 72,
              fontWeight: 700,
              color: "#2d2d2d",
              lineHeight: 1.1,
              maxWidth: 860,
            }}
          >
            2 minutes could save your life.
          </div>
          <div
            style={{
              fontSize: 28,
              color: "#6b6b6b",
              fontFamily: "system-ui, sans-serif",
              fontWeight: 400,
              maxWidth: 700,
            }}
          >
            Free oral cancer risk screener. Understand your risk, learn the
            signs, find care near you.
          </div>
        </div>

        {/* Bottom: URL + badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
          }}
        >
          <span
            style={{
              fontSize: 22,
              color: "#0d7377",
              fontFamily: "system-ui, sans-serif",
            }}
          >
            oralcheck.org
          </span>
          <div
            style={{
              display: "flex",
              gap: "12px",
              fontFamily: "system-ui, sans-serif",
              fontSize: 18,
              color: "#6b6b6b",
            }}
          >
            <span>✓ No account needed</span>
            <span>·</span>
            <span>✓ Nothing saved</span>
            <span>·</span>
            <span>✓ Takes 2 minutes</span>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}
