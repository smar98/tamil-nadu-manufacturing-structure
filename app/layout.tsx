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
  "Tamil Nadu employs more factory workers than any state in India and produces nearly the least value per worker. Three government surveys, read side by side and reconciled against the government's own published tables, on what that gap is - and what it is not.";

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
