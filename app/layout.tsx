import type { Metadata } from "next";
import { Libre_Franklin, Source_Serif_4 } from "next/font/google";
import "./globals.css";

const serif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

const franklin = Libre_Franklin({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-franklin",
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
    <html lang="en" className={`${serif.variable} ${franklin.variable}`}>
      <body>
        <script dangerouslySetInnerHTML={{ __html: "document.documentElement.classList.add('js');" }} />
        {children}
      </body>
    </html>
  );
}
