import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import Providers from '@/components/Providers';

export const metadata: Metadata = {
  title: {
    default: 'Easelos — Pre-Quoted Mechanical Parts Catalog',
    template: '%s | Easelos',
  },
  description:
    'Browse and download pre-quoted laser-cut mechanical parts with instant Ponoko pricing. STEP, SVG, and DXF files for mounting brackets, motor mounts, gusset plates, and more.',
  metadataBase: new URL('https://easelos.com'),
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <Providers>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
