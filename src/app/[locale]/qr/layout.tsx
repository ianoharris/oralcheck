import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Print & Share OralCheck | QR Code",
  description:
    "Download or print the OralCheck QR code to share at dental offices, community events, or waiting rooms. Free to use.",
  alternates: { canonical: "https://oralcheck.org/qr" },
};

export default function QRLayout({ children }: { children: React.ReactNode }) {
  return children;
}
