import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6 lg:px-8">
      <h1 className="text-4xl font-bold text-gray-900">404</h1>
      <p className="mt-4 text-lg text-gray-600">
        Part not found. It may have been removed or the URL is incorrect.
      </p>
      <div className="mt-8 flex justify-center gap-4">
        <Link
          href="/"
          className="rounded-md bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
        >
          Browse Catalog
        </Link>
        <Link
          href="/search/"
          className="rounded-md border border-gray-300 px-6 py-3 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
        >
          Search Parts
        </Link>
      </div>
    </div>
  );
}
