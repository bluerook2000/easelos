import Link from 'next/link';

export const metadata = {
  title: 'Forbidden',
  robots: { index: false },
};

export default function ForbiddenPage() {
  return (
    <div className="mx-auto max-w-md px-4 py-16 text-center sm:px-6 lg:px-8">
      <h1 className="text-6xl font-bold text-gray-300">403</h1>
      <h2 className="mt-4 text-xl font-semibold text-gray-900">Access Denied</h2>
      <p className="mt-2 text-gray-600">
        You do not have permission to access this page.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex items-center text-sm text-brand-600 hover:text-brand-700"
      >
        &larr; Return to catalog
      </Link>
    </div>
  );
}
