import type { Metadata } from "next";
import { Baloo_Tammudu_2 } from "next/font/google";
import "../styles/globals.css";

const baloo = Baloo_Tammudu_2({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-baloo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Verdant — Smarter Clean Energy",
  description:
    "Verdant empowers homeowners to harness clean energy intelligently. Reduce your emissions, lower your bills, and join a smarter grid.",
  keywords: ["clean energy", "sustainability", "solar", "green tech"],
  openGraph: {
    title: "Verdant — Smarter Clean Energy",
    description: "Empowering homes with intelligent clean energy solutions.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={baloo.variable}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body className="font-baloo bg-white text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
