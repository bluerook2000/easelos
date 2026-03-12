'use client';

import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';

export default function Navbar() {
  const { data: session } = useSession();

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
            {session?.user ? (
              <>
                <Link href="/vendor/dashboard/" className="text-sm text-gray-600 hover:text-gray-900">
                  Dashboard
                </Link>
                <button
                  onClick={() => signOut({ callbackUrl: '/' })}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <Link href="/auth/signin/" className="text-sm text-gray-600 hover:text-gray-900">
                Vendor Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
