import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { getDb, getPartById, getPartsByCategory, getRelatedParts } from '@/lib/db';
import { generatePartTitle, generatePartDescription, generateProductJsonLd } from '@/lib/seo';
import PricingTable from '@/components/PricingTable';
import DownloadButtons from '@/components/DownloadButtons';
import PartSpecs from '@/components/PartSpecs';
import PartCard from '@/components/PartCard';
import BreadcrumbNav from '@/components/BreadcrumbNav';
import { CATEGORY_NAMES } from '@/lib/constants';

interface PageProps {
  params: { category: string; partId: string };
}

export function generateStaticParams() {
  try {
    const db = getDb();
    const categories = Object.keys(CATEGORY_NAMES);
    const params: Array<{ category: string; partId: string }> = [];
    for (const category of categories) {
      const parts = getPartsByCategory(db, category);
      for (const part of parts) {
        params.push({ category, partId: part.part_id });
      }
    }
    return params;
  } catch {
    return [];
  }
}

export function generateMetadata({ params }: PageProps): Metadata {
  try {
    const db = getDb();
    const part = getPartById(db, params.partId);
    if (!part) return { title: 'Part Not Found' };

    return {
      title: generatePartTitle(part),
      description: generatePartDescription(part),
      alternates: {
        canonical: `/parts/${part.category}/${part.part_id}/`,
      },
    };
  } catch {
    return { title: 'Part Not Found' };
  }
}

export default function PartDetailPage({ params }: PageProps) {
  const db = getDb();
  const part = getPartById(db, params.partId);
  if (!part) notFound();

  const categoryName = CATEGORY_NAMES[part.category] || part.category;
  const jsonLd = generateProductJsonLd(part);
  const relatedParts = getRelatedParts(db, part, 4);

  return (
    <>
      {/* JSON-LD structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BreadcrumbNav
          items={[
            { label: categoryName, href: `/parts/${part.category}/` },
            { label: part.name },
          ]}
        />

        {/* Main content */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Left: SVG preview */}
          <div>
            <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-gray-50 p-8">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`/parts/${part.category}/${part.part_id}/profile.svg`}
                alt={part.name}
                className="max-h-80 w-full object-contain"
              />
            </div>

            {/* Downloads */}
            <div className="mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Download Files</h2>
              <DownloadButtons category={part.category} partId={part.part_id} />
            </div>

            {/* Order on Ponoko */}
            <div className="mt-4">
              <a
                href="https://www.ponoko.com/laser-cutting"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-sm text-brand-600 hover:text-brand-700"
              >
                Order on Ponoko &rarr;
              </a>
            </div>
          </div>

          {/* Right: Details */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{part.name}</h1>
            <p className="mt-2 text-gray-600">{part.description}</p>

            {/* Pricing */}
            <div className="mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Pricing</h2>
              <PricingTable pricing={part.pricing} defaultMaterial={part.material} />
            </div>

            {/* Specs */}
            <div className="mt-6">
              <PartSpecs
                width_mm={part.width_mm}
                height_mm={part.height_mm}
                thickness_mm={part.thickness_mm}
                weight_estimate_g={part.weight_estimate_g}
                material_name={part.material_name}
                hole_count={part.hole_count}
                hole_specs={part.hole_specs}
                complexity={part.complexity}
                size_category={part.size_category}
              />
            </div>

            {/* Vendor CTA */}
            <div className="mt-8">
              <a
                href={`/api/vendor/interest?part_id=${part.part_id}&category=${part.category}`}
                className="inline-flex items-center rounded-md bg-gray-900 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-gray-800"
              >
                I Can Make This
              </a>
              <p className="mt-2 text-xs text-gray-500">
                Are you a manufacturer? Register to express interest.
              </p>
            </div>
          </div>
        </div>

        {/* Related parts */}
        {relatedParts.length > 0 && (
          <section className="mt-16">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">Related Parts</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {relatedParts.map((p) => (
                <PartCard key={p.part_id} part={p} />
              ))}
            </div>
          </section>
        )}
      </div>
    </>
  );
}
