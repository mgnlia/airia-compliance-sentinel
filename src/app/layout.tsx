import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Compliance Sentinel",
  description: "Multi-Agent RegTech Compliance Monitoring",
};

function NavLink({ href, label }: { href: string; label: string }) {
  return <a href={href} className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 transition-colors">{label}</a>;
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-sentinel-bg">
        <nav className="border-b border-sentinel-border bg-sentinel-card/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🛡️</span>
                <span className="text-lg font-bold text-white">Compliance Sentinel</span>
              </div>
              <div className="flex gap-1">
                <NavLink href="/" label="Dashboard" />
                <NavLink href="/findings" label="Findings" />
                <NavLink href="/reviews" label="Reviews" />
                <NavLink href="/analyze" label="Analyze" />
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
      </body>
    </html>
  );
}
