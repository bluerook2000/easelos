import Link from 'next/link';
import type { Part } from '@/lib/types';

export default function PartCard({ part }: { part: Part }) {
  const price = part.pricing[part.material]?.['1'];
  return (
    <Link
      href={`/parts/${part.category}/${part.part_id}/`}
      className="group rounded-lg border border-gray-200 p-4 transition-colors hover:border-brand-500"
    >
      {/* SVG thumbnail */}
      <div className="mb-3 flex h-32 items-center justify-center overflow-hidden rounded bg-gray-50">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`/parts/${part.category}/${part.part_id}/profile.svg`}
          alt={part.name}
          className="max-h-full max-w-full object-contain"
          loading="lazy"
        />
      </div>
      <h3 className="text-sm font-medium text-gray-900 group-hover:text-brand-700 line-clamp-2">
        {part.name}
      </h3>
      <p className="mt-1 text-xs text-gray-500">
        {part.width_mm}x{part.height_mm}x{part.thickness_mm}mm
      </p>
      {price && (
        <p className="mt-1 text-sm font-semibold text-brand-600">
          From ${price.toFixed(2)}
        </p>
      )}
    </Link>
  );
}
