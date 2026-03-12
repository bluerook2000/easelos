import Link from 'next/link';

export const metadata = {
  title: 'Check Your Email',
  robots: { index: false },
};

export default function VerifyRequestPage() {
  return (
    <div className="mx-auto max-w-md px-4 py-16 text-center sm:px-6 lg:px-8">
      <div className="mx-auto h-16 w-16 rounded-full bg-brand-50 flex items-center justify-center">
        <svg className="h-8 w-8 text-brand-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
        </svg>
      </div>
      <h1 className="mt-6 text-2xl font-bold text-gray-900">Check Your Email</h1>
      <p className="mt-4 text-gray-600">
        A sign-in link has been sent to your email address.
        Click the link to continue.
      </p>
      <p className="mt-2 text-sm text-gray-500">
        If you do not see the email, check your spam folder.
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
