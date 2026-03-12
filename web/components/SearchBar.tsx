'use client';

import { useState, useEffect, useCallback } from 'react';
import type { SearchEntry } from '@/lib/search';
import { searchParts } from '@/lib/search';

interface SearchBarProps {
  onResults: (results: SearchEntry[]) => void;
  initialQuery?: string;
}

export default function SearchBar({ onResults, initialQuery = '' }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [index, setIndex] = useState<SearchEntry[] | null>(null);

  useEffect(() => {
    fetch('/search-index.json')
      .then((r) => r.json())
      .then((data: SearchEntry[]) => {
        setIndex(data);
      })
      .catch(() => {
        // Index not available
      });
  }, []);

  const doSearch = useCallback(
    (q: string) => {
      if (!index) return;
      const results = searchParts(index, q);
      onResults(results);
    },
    [index, onResults],
  );

  useEffect(() => {
    if (index) {
      doSearch(query);
    }
  }, [index, query, doSearch]);

  return (
    <input
      type="search"
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);
      }}
      placeholder="Search parts (e.g., aluminum bracket M5, NEMA 23 motor mount)"
      className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      autoFocus
    />
  );
}
