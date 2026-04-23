import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Find Dental Care Near You | OralCheck",
  description:
    "Locate dentists, community health centers, and free dental clinics near you. Filter by distance and clinic type. No account needed.",
};

export default function FindCareLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
