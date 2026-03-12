import type { Part } from './types';
import { CATEGORY_LABELS } from './constants';

export function generatePartTitle(part: Part): string {
  const materialShort = part.material_name.split(' ').pop() || part.material;
  const partType = CATEGORY_LABELS[part.category] || part.category;
  const specs = `${part.width_mm}x${part.height_mm}mm`;
  const holes = part.hole_count > 0
    ? ` ${part.hole_count}-Hole`
    : '';
  return `${materialShort} ${partType} ${specs}${holes} | Laser Cut | Easelos`;
}

export function generatePartDescription(part: Part): string {
  const price = part.pricing[part.material]?.['1'] ?? 'N/A';
  const desc = `${part.name} - ${part.width_mm}x${part.height_mm}x${part.thickness_mm}mm. From $${price} ea. Download STEP, SVG, DXF. Instant Ponoko pricing.`;
  return desc.slice(0, 160);
}

export function generateProductJsonLd(part: Part): Record<string, any> {
  const price = part.pricing[part.material]?.['1'] ?? 0;
  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: part.name,
    description: part.description,
    sku: part.part_id,
    image: `https://easelos.com/parts/${part.category}/${part.part_id}/thumbnail.png`,
    offers: {
      '@type': 'Offer',
      price: String(price),
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: `https://easelos.com/parts/${part.category}/${part.part_id}/`,
    },
    brand: {
      '@type': 'Brand',
      name: 'Easelos',
    },
    material: part.material_name,
    weight: {
      '@type': 'QuantitativeValue',
      value: part.weight_estimate_g,
      unitCode: 'GRM',
    },
  };
}
