import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Oral Cancer Risk Screener | OralCheck";
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
            Free · Private
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
              Know your oral<br />cancer risk.
            </div>
            <div style={{ fontSize: 24, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
              10 questions. 2 minutes.<br />No account. Nothing saved.
            </div>
          </div>

          {/* Steps */}
          <div style={{ display: "flex", flexDirection: "column", gap: "14px", flexShrink: 0 }}>
            {["Answer 10 questions", "Get your risk tier", "See your next steps"].map((s, i) => (
              <div
                key={s}
                style={{ display: "flex", alignItems: "center", gap: "12px", fontFamily: "system-ui, sans-serif", fontSize: 16, color: "#2d2d2d" }}
              >
                <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: "#0d7377", color: "#fff", fontSize: 13, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  {i + 1}
                </div>
                {s}
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
          <span style={{ fontSize: 20, color: "#0d7377", fontFamily: "system-ui, sans-serif" }}>oralcheck.org</span>
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>Informed by ACS · NCI · Oral Cancer Foundation</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
