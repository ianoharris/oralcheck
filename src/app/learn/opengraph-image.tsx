import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Learn About Oral Cancer | OralCheck";
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
            Learn
          </div>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            padding: "48px 72px",
            gap: "60px",
          }}
        >
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 64, fontWeight: 700, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 20 }}>
              Learn about<br />oral cancer.
            </div>
            <div style={{ fontSize: 24, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
              Evidence-based guides written for<br />regular people, not clinicians.
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", flexShrink: 0 }}>
            {[
              ["⚠️", "Warning signs"],
              ["🔎", "Self-exam guide"],
              ["🦠", "HPV and oral cancer"],
              ["🛡️", "Prevention"],
              ["📊", "Facts & stats"],
            ].map(([icon, label]) => (
              <div
                key={label}
                style={{ display: "flex", alignItems: "center", gap: "10px", fontFamily: "system-ui, sans-serif", fontSize: 15, color: "#2d2d2d" }}
              >
                <span style={{ fontSize: 18 }}>{icon}</span>
                {label}
              </div>
            ))}
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
          <span style={{ fontSize: 20, color: "#0d7377", fontFamily: "system-ui, sans-serif" }}>oralcheck.org/learn</span>
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>Free · No account needed</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
