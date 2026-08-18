import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

// Security headers live here rather than in vercel.json so they apply to `next
// dev` too. That is not tidiness: a CSP that only exists in the hosting config
// cannot be tested before it reaches production, and an over-tight CSP takes
// the site down. This one was checked against the running app.
//
// 'unsafe-inline' and 'unsafe-eval' in script-src are a real weakening, and
// they are here because Next's hydration and the GA snippet both inject inline
// script without a nonce. What the policy still buys: script cannot be loaded
// from an origin that is not listed, so an injected <script src> to an
// attacker host is blocked, as is form-action off-site, base-tag injection,
// plugin content, and framing by another origin.
const CSP = [
  "default-src 'self'",
  // va.vercel-scripts.com is @vercel/analytics, injected at runtime rather than
  // present in the served HTML. Only the browser check caught it.
  "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://w.behold.so https://va.vercel-scripts.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' data: https://fonts.gstatic.com",
  // Map tiles, Instagram thumbnails and article imagery come from a long tail
  // of hosts; images are a low-risk sink, so this stays broad on purpose.
  "img-src 'self' data: blob: https:",
  "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com https://*.behold.so https://*.tile.openstreetmap.org https://va.vercel-scripts.com https://vitals.vercel-insights.com",
  "frame-src 'self' https://www.instagram.com",
  "worker-src 'self' blob:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'self'",
  "upgrade-insecure-requests",
].join("; ");

const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Content-Security-Policy", value: CSP },
];

const nextConfig: NextConfig = {
  async headers() {
    return [
      { source: "/:path*", headers: SECURITY_HEADERS },
      {
        // API responses are per-request and some are personalised. Nothing
        // should cache them, and none of them belong in a search index.
        source: "/api/:path*",
        headers: [
          { key: "Cache-Control", value: "no-store" },
          { key: "X-Robots-Tag", value: "noindex" },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
