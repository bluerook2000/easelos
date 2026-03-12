import type { Metadata } from 'next';
import { Suspense } from 'react';
import VendorRegistrationForm from '@/components/VendorRegistrationForm';

export const metadata: Metadata = {
  title: 'Vendor Registration',
  description: 'Register as a manufacturing vendor on Easelos.',
  robots: { index: false },
};

export default function VendorRegisterPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Vendor Registration</h1>
        <p className="mt-2 text-gray-600">
          Register your manufacturing capabilities. Your profile is only visible
          to Easelos administrators.
        </p>
      </div>
      <Suspense fallback={<div className="text-center py-8 text-gray-500">Loading form...</div>}>
        <VendorRegistrationForm />
      </Suspense>
    </div>
  );
}
