import { describe, it, expect } from 'vitest';
import { generatePartTitle, generatePartDescription, generateProductJsonLd } from '../lib/seo';
import type { Part } from '../lib/types';

const testPart: Part = {
  part_id: 'mounting_bracket-flat-30x20x1.6-4xM5-aluminum',
  category: 'mounting_bracket',
  name: '5052-H32 Aluminum Flat Bracket 30x20mm 4xM5',
  description: 'Laser-cut flat mounting bracket.',
  width_mm: 30, height_mm: 20, thickness_mm: 1.6,
  width_in: 1.18, height_in: 0.79, area_sq_in: 0.93,
  hole_count: 4,
  hole_specs: [{ size: 'M5', diameter_mm: 5.5, x_mm: -7, y_mm: -2 }],
  material: 'aluminum', material_name: '5052-H32 Aluminum',
  weight_estimate_g: 2.57, complexity: 'moderate', size_category: 'small',
  pricing: {
    aluminum: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
    steel: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
    stainless: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
  },
  files: { step: 'part.step', svg: 'profile.svg', dxf: 'profile.dxf', png: 'thumbnail.png', metadata: 'metadata.json' },
};

describe('SEO helpers', () => {
  it('generates title matching spec format', () => {
    const title = generatePartTitle(testPart);
    expect(title).toContain('Aluminum');
    expect(title).toContain('Bracket');
    expect(title).toContain('Laser Cut');
    expect(title).toContain('Easelos');
    expect(title).toContain('|');
  });

  it('generates meta description with price and dimensions', () => {
    const desc = generatePartDescription(testPart);
    expect(desc).toContain('13.55');
    expect(desc).toContain('30');
    expect(desc).toContain('20');
    expect(desc.length).toBeLessThanOrEqual(160);
  });

  it('generates valid Product JSON-LD', () => {
    const jsonLd = generateProductJsonLd(testPart);
    expect(jsonLd['@context']).toBe('https://schema.org');
    expect(jsonLd['@type']).toBe('Product');
    expect(jsonLd.name).toBe(testPart.name);
    expect(jsonLd.sku).toBe(testPart.part_id);
    expect(jsonLd.offers).toBeDefined();
    expect(jsonLd.offers['@type']).toBe('Offer');
    expect(jsonLd.offers.price).toBe('13.55');
    expect(jsonLd.offers.priceCurrency).toBe('USD');
    expect(jsonLd.image).toContain(testPart.part_id);
  });

  it('JSON-LD includes description', () => {
    const jsonLd = generateProductJsonLd(testPart);
    expect(jsonLd.description).toBe(testPart.description);
  });
});
