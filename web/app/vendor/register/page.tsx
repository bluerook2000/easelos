import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Vendor Registration',
  description: 'Register as a manufacturing vendor on Easelos.',
};

export default function VendorRegisterPage() {
  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-900">Vendor Registration</h1>
      <p className="mt-4 text-lg text-gray-600">
        Coming soon. We are building a vendor portal where manufacturers can
        register their capabilities and express interest in making parts from
        our catalog.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex items-center rounded-md bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
      >
        Browse the Catalog
      </Link>
    </div>
  );
}
