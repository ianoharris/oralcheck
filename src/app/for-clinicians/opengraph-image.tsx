import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "OralCheck — For Dental Professionals";
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
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#e8634a" }} />
          <span style={{ fontSize: 28, color: "#fff", fontWeight: 700 }}>OralCheck</span>
          <div
            style={{
              background: "rgba(255,255,255,0.2)",
              color: "#fff",
              fontSize: 14,
              fontWeight: 600,
              padding: "5px 16px",
              borderRadius: 999,
              fontFamily: "system-ui, sans-serif",
              marginLeft: 8,
            }}
          >
            For Dental Professionals
          </div>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            padding: "48px 72px",
            gap: "64px",
          }}
        >
          {/* Left: headline */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 52, fontWeight: 700, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 20 }}>
              Help your patients<br />
              take 2 minutes<br />
              <span style={{ color: "#0d7377" }}>that could save</span><br />
              their life.
            </div>
            <div style={{ fontSize: 20, color: "#6b6b6b", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
              Free printable flyer. No setup. No PHI.
            </div>
          </div>

          {/* Right: feature tiles */}
          <div style={{ display: "flex", flexDirection: "column", gap: 14, flexShrink: 0, width: 260 }}>
            {[
              { icon: "🔒", label: "Zero PHI collected" },
              { icon: "✓",  label: "No login or setup" },
              { icon: "🆓", label: "Free, permanently" },
              { icon: "🖨️", label: "Printable waiting room flyer" },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  background: "#fff",
                  border: "1px solid #e8e4de",
                  borderRadius: 12,
                  padding: "14px 20px",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                <span style={{ fontSize: 22 }}>{item.icon}</span>
                <span style={{ fontSize: 16, color: "#2d2d2d", fontWeight: 600 }}>{item.label}</span>
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
          <span style={{ fontSize: 20, color: "#0d7377", fontFamily: "system-ui, sans-serif" }}>
            oralcheck.org/for-clinicians
          </span>
          <span style={{ fontSize: 16, color: "#aaa", fontFamily: "system-ui, sans-serif" }}>
            Evidence-based · Free · Private
          </span>
        </div>
      </div>
    ),
    { ...size },
  );
}
