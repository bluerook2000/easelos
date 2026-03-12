import type { Metadata } from 'next';
import SearchResults from '@/components/SearchResults';

export const metadata: Metadata = {
  title: 'Search Parts',
  description: 'Search the Easelos catalog of pre-quoted laser-cut mechanical parts.',
};

export default function SearchPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Search Parts</h1>
      <SearchResults />
    </div>
  );
}
