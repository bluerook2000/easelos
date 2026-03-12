import Link from 'next/link';
import type { CategorySummary } from '@/lib/types';

export default function CategoryCard({ category }: { category: CategorySummary }) {
  return (
    <Link
      href={`/parts/${category.slug}/`}
      className="group rounded-lg border border-gray-200 p-6 transition-colors hover:border-brand-500 hover:bg-brand-50"
    >
      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-brand-700">
        {category.name}
      </h3>
      <p className="mt-1 text-sm text-gray-500">{category.description}</p>
      <p className="mt-3 text-sm font-medium text-brand-600">
        {category.part_count} parts
      </p>
    </Link>
  );
}
