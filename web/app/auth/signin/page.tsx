import type { Metadata } from 'next';
import { Suspense } from 'react';
import SignInForm from './SignInForm';

export const metadata: Metadata = {
  title: 'Sign In',
  robots: { index: false },
};

export default function SignInPage() {
  return (
    <Suspense fallback={<div className="mx-auto max-w-md px-4 py-16 text-center">Loading...</div>}>
      <SignInForm />
    </Suspense>
  );
}
