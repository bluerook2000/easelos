'use client';

import { useState, useCallback } from 'react';
import SearchBar from './SearchBar';
import type { SearchEntry } from '@/lib/search';
import { CATEGORY_NAMES } from '@/lib/constants';
import Link from 'next/link';

export default function SearchResults() {
  const [results, setResults] = useState<SearchEntry[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleResults = useCallback((r: SearchEntry[]) => {
    setResults(r);
    setHasSearched(true);
  }, []);

  return (
    <div>
      <SearchBar onResults={handleResults} />

      {hasSearched && (
        <div className="mt-6">
          <p className="mb-4 text-sm text-gray-500">
            {results.length} result{results.length !== 1 ? 's' : ''}
          </p>

          <div className="space-y-3">
            {results.map((r) => (
              <Link
                key={r.id}
                href={`/parts/${r.c}/${r.id}/`}
                className="block rounded-lg border border-gray-200 p-4 hover:border-brand-500 hover:bg-brand-50 transition-colors"
              >
                <p className="font-medium text-gray-900">{r.n}</p>
                <p className="mt-1 text-sm text-gray-500">
                  {CATEGORY_NAMES[r.c] || r.c} &middot; {r.m}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
