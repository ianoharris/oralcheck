import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Warning Signs of Oral Cancer | OralCheck";
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
          fontFamily: "Georgia, serif",
        }}
      >
        {/* Teal top band */}
        <div
          style={{
            background: "#0d7377",
            padding: "32px 72px",
            display: "flex",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <div style={{ width: "14px", height: "14px", borderRadius: "50%", background: "#e8634a" }} />
          <span style={{ fontSize: 28, color: "#fff", fontWeight: 700 }}>OralCheck</span>
          <div
            style={{
              background: "rgba(255,255,255,0.2)",
              color: "#fff",
              fontSize: 14,
              fontWeight: 600,
              padding: "5px 14px",
              borderRadius: "999px",
              fontFamily: "system-ui, sans-serif",
              marginLeft: 8,
            }}
          >
            Symptoms
          </div>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            padding: "48px 72px",
          }}
        >
          <div style={{ fontSize: 64, fontWeight: 700, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 20 }}>
            Warning Signs of<br />Oral Cancer
          </div>
          <div style={{ fontSize: 26, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", fontWeight: 400, lineHeight: 1.5 }}>
            A sore that won't heal. A patch on your tongue. A lump you can't explain.<br />
            If it's been there 2 weeks — get it checked.
          </div>
        </div>

        {/* Bottom bar */}
        <div
          style={{
            padding: "24px 72px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderTop: "1px solid #e8e4de",
          }}
        >
          <span style={{ fontSize: 20, color: "#0d7377", fontFamily: "system-ui, sans-serif" }}>oralcheck.org</span>
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>Free · Private · 2 minutes</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
