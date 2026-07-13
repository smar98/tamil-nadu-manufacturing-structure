import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://smar98.github.io/tamil-nadu-manufacturing-structure/";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Tamil Nadu Manufacturing: A Structural Snapshot",
  description: "A reproducible comparison of enterprise scale, labor productivity and employment form in Tamil Nadu manufacturing.",
  openGraph: {
    type: "website",
    url: siteUrl,
    title: "Tamil Nadu Manufacturing: A Structural Snapshot",
    description: "Three official surveys show how Tamil Nadu manufacturing is organized across enterprise types.",
    images: [{ url: `${siteUrl}og.png`, width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Tamil Nadu Manufacturing: A Structural Snapshot",
    description: "Three official surveys show how Tamil Nadu manufacturing is organized across enterprise types.",
    images: [`${siteUrl}og.png`],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
