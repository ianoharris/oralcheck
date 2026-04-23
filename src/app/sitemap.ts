import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://oralcheck.org";

  return [
    {
      url: base,
      lastModified: new Date("2024-12-01"),
      changeFrequency: "monthly",
      priority: 1,
    },
    {
      url: `${base}/screener`,
      lastModified: new Date("2024-12-01"),
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${base}/learn`,
      lastModified: new Date("2026-04-23"),
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${base}/learn/signs`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${base}/learn/self-exam`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/learn/facts`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${base}/learn/hpv`,
      lastModified: new Date("2026-04-23"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/learn/prevention`,
      lastModified: new Date("2026-04-23"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/learn/canker-sore-vs-oral-cancer`,
      lastModified: new Date("2026-04-23"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/find-care`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/about`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${base}/qr`,
      lastModified: new Date("2025-01-01"),
      changeFrequency: "yearly",
      priority: 0.4,
    },
  ];
}
