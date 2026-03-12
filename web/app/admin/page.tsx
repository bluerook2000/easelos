import type { Metadata } from 'next';
import AdminVendorList from '@/components/AdminVendorList';

export const metadata: Metadata = {
  title: 'Admin — Vendors',
  robots: { index: false },
};

export default function AdminPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-900">Vendor Management</h1>
      <p className="mt-2 text-gray-600">
        View and filter all registered vendors.
      </p>
      <div className="mt-8">
        <AdminVendorList />
      </div>
    </div>
  );
}
