import type { Metadata } from 'next';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '@/lib/auth';
import { getVendorDb, getVendorByEmail, getVendorInterests } from '@/lib/vendor-db';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Vendor Dashboard',
  robots: { index: false },
};

export default async function VendorDashboardPage() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    redirect('/auth/signin?callbackUrl=/vendor/dashboard');
  }

  const db = getVendorDb();
  const vendor = getVendorByEmail(db, session.user.email);

  if (!vendor) {
    redirect('/vendor/register');
  }

  const interests = getVendorInterests(db, vendor.id);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Vendor Dashboard</h1>
        <Link
          href="/vendor/register"
          className="text-sm text-brand-600 hover:text-brand-700"
        >
          Edit Profile
        </Link>
      </div>

      {/* Profile Summary */}
      <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-gray-900">{vendor.company_name}</h2>
        <p className="mt-1 text-sm text-gray-500">
          {vendor.contact_name} &middot; {vendor.email}
        </p>
        {(vendor.city || vendor.state || vendor.country) && (
          <p className="mt-1 text-sm text-gray-500">
            {[vendor.city, vendor.state, vendor.country].filter(Boolean).join(', ')}
          </p>
        )}

        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div>
            <h3 className="text-xs font-medium uppercase text-gray-500">Capacity</h3>
            <p className="text-sm text-gray-900">{vendor.capacity}</p>
          </div>
          <div>
            <h3 className="text-xs font-medium uppercase text-gray-500">Lead Time</h3>
            <p className="text-sm text-gray-900">{vendor.lead_time}</p>
          </div>
          <div>
            <h3 className="text-xs font-medium uppercase text-gray-500">Machines</h3>
            <p className="text-sm text-gray-900">{vendor.machines.length}</p>
          </div>
        </div>

        {vendor.materials.length > 0 && (
          <div className="mt-4">
            <h3 className="text-xs font-medium uppercase text-gray-500">Materials</h3>
            <div className="mt-1 flex flex-wrap gap-1">
              {vendor.materials.map((m) => (
                <span key={m} className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}

        {vendor.certifications.length > 0 && (
          <div className="mt-4">
            <h3 className="text-xs font-medium uppercase text-gray-500">Certifications</h3>
            <div className="mt-1 flex flex-wrap gap-1">
              {vendor.certifications.map((c) => (
                <span key={c} className="inline-flex rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                  {c}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Parts of Interest */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900">Parts of Interest</h2>
        {interests.length === 0 ? (
          <div className="mt-4 rounded-lg border border-dashed border-gray-300 p-8 text-center">
            <p className="text-gray-500">No parts yet.</p>
            <Link href="/" className="mt-2 inline-flex text-sm text-brand-600 hover:text-brand-700">
              Browse the catalog &rarr;
            </Link>
          </div>
        ) : (
          <div className="mt-4 space-y-2">
            {interests.map((interest) => (
              <div key={interest.part_id} className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3">
                <Link
                  href={`/parts/${interest.category}/${interest.part_id}/`}
                  className="text-sm font-medium text-brand-600 hover:text-brand-700"
                >
                  {interest.part_id}
                </Link>
                <span className="text-xs text-gray-500">
                  {new Date(interest.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
