import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Find Oral Cancer Care Near You",
  description:
    "Find dentists, community health centers, and free clinics near you that offer oral cancer screenings. Filter by type and distance. No account needed.",
  alternates: { canonical: "https://oralcheck.org/find-care" },
};

export default function FindCareLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
