import type { Metadata } from "next";
import { Archivo, Newsreader } from "next/font/google";
import "./globals.css";

// opsz must be declared explicitly, or every size renders in Newsreader's 16pt
// text cut and the display headings read flat.
const serif = Newsreader({
  subsets: ["latin"],
  axes: ["opsz"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

// Archivo replaces Libre Franklin, which shipped no tabular figures at all -- so
// the ledger's `font-variant-numeric: tabular-nums` was a silent no-op and the
// exhibit columns never actually aligned. Archivo's tnum really does shape all
// ten digits to one width (verified with HarfBuzz, not from the feature tag:
// Golos Text advertises tnum and still returns five different widths).
const ui = Archivo({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--font-ui",
  display: "swap",
});

const siteUrl = "https://smar98.github.io/tamil-nadu-manufacturing-structure/";
const title = "India's Factory State: Tamil Nadu's Manufacturing Paradox, 2023-24";
const description =
  "Tamil Nadu employs more registered-factory workers than any Indian state, yet its factories add less value per person (GVA per person engaged) than any of the areas this page compares it with. Three official surveys, checked against 28 pre-declared published benchmarks, show what that gap is - and what it is not.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title,
  description,
  openGraph: {
    type: "website",
    url: siteUrl,
    title,
    description,
    images: [{ url: `${siteUrl}og.png`, width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: [`${siteUrl}og.png`],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${serif.variable} ${ui.variable}`}>
      <body>
        <script dangerouslySetInnerHTML={{ __html: "document.documentElement.classList.add('js');" }} />
        {children}
      </body>
    </html>
  );
}
