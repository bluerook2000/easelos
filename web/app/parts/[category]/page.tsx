import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { getDb, getAllCategories, getPartsByCategory } from '@/lib/db';
import { CATEGORY_NAMES } from '@/lib/constants';
import PartCard from '@/components/PartCard';
import BreadcrumbNav from '@/components/BreadcrumbNav';

interface PageProps {
  params: { category: string };
}

export function generateStaticParams() {
  try {
    const db = getDb();
    const categories = getAllCategories(db);
    return categories.map((c) => ({ category: c.slug }));
  } catch {
    return [];
  }
}

export function generateMetadata({ params }: PageProps): Metadata {
  const name = CATEGORY_NAMES[params.category] || params.category;
  return {
    title: `${name} | Laser Cut Parts`,
    description: `Browse laser-cut ${name.toLowerCase()} with instant Ponoko pricing. Download STEP, SVG, and DXF files.`,
  };
}

export default function CategoryPage({ params }: PageProps) {
  const db = getDb();
  const categoryName = CATEGORY_NAMES[params.category];
  if (!categoryName) notFound();

  const parts = getPartsByCategory(db, params.category);
  if (parts.length === 0) notFound();

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <BreadcrumbNav items={[{ label: categoryName }]} />

      <h1 className="text-3xl font-bold text-gray-900">{categoryName}</h1>
      <p className="mt-2 text-gray-600">{parts.length} parts available</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {parts.map((part) => (
          <PartCard key={part.part_id} part={part} />
        ))}
      </div>
    </div>
  );
}
