import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="text-xl font-bold text-brand-900">
            Easelos
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
              Catalog
            </Link>
            <Link href="/search/" className="text-sm text-gray-600 hover:text-gray-900">
              Search
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
