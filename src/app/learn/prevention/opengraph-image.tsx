import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "How to Prevent Oral Cancer | OralCheck";
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
            Prevention
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
          {/* Left: headline */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 64, fontWeight: 700, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 16 }}>
              How to Prevent<br />Oral Cancer
            </div>
            <div style={{ fontSize: 22, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
              The biggest risk factors are modifiable.<br />
              Here's what the evidence actually supports.
            </div>
          </div>

          {/* Right: checklist */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px", flexShrink: 0 }}>
            {[
              "Quit tobacco",
              "Limit alcohol",
              "HPV vaccine",
              "Regular dental visits",
              "Protect your lips",
              "Monthly self-exam",
            ].map((item) => (
              <div
                key={item}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  fontFamily: "system-ui, sans-serif",
                  fontSize: 16,
                  color: "#2d2d2d",
                }}
              >
                <div style={{ width: "20px", height: "20px", borderRadius: "50%", background: "#0d7377", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#fff" }} />
                </div>
                {item}
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
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>Free · Private · 2 minutes</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
