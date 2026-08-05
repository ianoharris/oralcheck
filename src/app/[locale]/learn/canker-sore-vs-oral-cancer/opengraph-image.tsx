import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Canker Sore vs Oral Cancer: How to Tell the Difference | OralCheck";
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
            Guide
          </div>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            padding: "48px 72px",
            gap: "56px",
          }}
        >
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 56, fontWeight: 700, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 20 }}>
              Canker Sore<br />vs Oral Cancer
            </div>
            <div style={{ fontSize: 22, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
              Canker sores heal in 7–10 days.<br />Oral cancer doesn't.<br />Here's how to tell them apart.
            </div>
          </div>

          {/* Key rule */}
          <div style={{ flexShrink: 0, display: "flex", flexDirection: "column", gap: "14px" }}>
            <div style={{ background: "#fff", border: "1px solid #e8e4de", borderRadius: "16px", padding: "18px 24px", maxWidth: "240px" }}>
              <div style={{ fontSize: 13, fontFamily: "system-ui, sans-serif", fontWeight: 700, color: "#4caf50", marginBottom: 6 }}>CANKER SORE</div>
              <div style={{ fontSize: 14, fontFamily: "system-ui, sans-serif", color: "#2d2d2d", lineHeight: 1.4 }}>Painful · Round · Heals in 7–14 days</div>
            </div>
            <div style={{ background: "#fff", border: "1px solid #e8e4de", borderRadius: "16px", padding: "18px 24px", maxWidth: "240px" }}>
              <div style={{ fontSize: 13, fontFamily: "system-ui, sans-serif", fontWeight: 700, color: "#e8634a", marginBottom: 6 }}>WATCH OUT FOR</div>
              <div style={{ fontSize: 14, fontFamily: "system-ui, sans-serif", color: "#2d2d2d", lineHeight: 1.4 }}>Painless · Irregular · Won't heal after 2 weeks</div>
            </div>
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
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>Free · No account needed</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
