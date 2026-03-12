import fs from 'fs';
import path from 'path';
import GrowthChart from '@/components/GrowthChart';
import CategoryCard from '@/components/CategoryCard';
import type { GrowthEntry, CategorySummary } from '@/lib/types';
import { getDb, getAllCategories, getPartCount } from '@/lib/db';
import Link from 'next/link';

function getGrowthData(): GrowthEntry[] {
  const logPath = path.join(process.cwd(), 'data', 'growth-log.json');
  if (!fs.existsSync(logPath)) return [];
  return JSON.parse(fs.readFileSync(logPath, 'utf-8'));
}

export default function HomePage() {
  let categories: CategorySummary[] = [];
  let totalParts = 0;
  let growthData: GrowthEntry[] = [];

  try {
    const db = getDb();
    categories = getAllCategories(db);
    totalParts = getPartCount(db);
    growthData = getGrowthData();
  } catch {
    // Database not yet built — show placeholder
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Hero */}
      <section className="mb-16 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Pre-Quoted Mechanical Parts
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
          Browse {totalParts.toLocaleString()} laser-cut parts with instant Ponoko pricing.
          Download STEP, SVG, and DXF files. Ready to order.
        </p>
        <div className="mt-6">
          <Link
            href="/search/"
            className="inline-flex items-center rounded-md bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
          >
            Search Parts
          </Link>
        </div>
      </section>

      {/* Growth Chart */}
      {growthData.length > 0 && (
        <section className="mb-16">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">Catalog Growth</h2>
          <GrowthChart data={growthData} />
        </section>
      )}

      {/* Category Grid */}
      <section>
        <h2 className="mb-6 text-xl font-semibold text-gray-900">Browse by Category</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat) => (
            <CategoryCard key={cat.slug} category={cat} />
          ))}
        </div>
      </section>
    </div>
  );
}
