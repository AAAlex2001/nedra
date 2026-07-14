import type { Metadata } from "next";
import Header from "@/widgets/header";
import "./globals.scss";

export const metadata: Metadata = {
  title: "Nedra",
  description: "Nedra frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>
        <Header />
        {children}
      </body>
    </html>
  );
}
