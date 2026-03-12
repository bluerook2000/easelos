import { describe, it, expect } from 'vitest';
import type { PartPricing } from '../lib/types';

const testPricing: PartPricing = {
  aluminum: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
  steel: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
  stainless: { '1': 20.22, '10': 6.64, '100': 3.45, '500': 2.47, '1000': 2.15, '10000': 1.07 },
};

const MATERIALS = ['aluminum', 'steel', 'stainless'] as const;
const QUANTITIES = ['1', '10', '100', '500', '1000', '10000'] as const;

function getPriceForMaterialAndQty(
  pricing: PartPricing,
  material: string,
  quantity: string,
): number | null {
  return pricing[material]?.[quantity] ?? null;
}

function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`;
}

function getMaterialLabel(slug: string): string {
  const labels: Record<string, string> = {
    aluminum: '5052-H32 Aluminum',
    steel: 'A1011 Carbon Steel',
    stainless: '304 Stainless Steel',
  };
  return labels[slug] || slug;
}

describe('Pricing display logic', () => {
  it('retrieves correct price for material and quantity', () => {
    expect(getPriceForMaterialAndQty(testPricing, 'aluminum', '1')).toBe(13.55);
    expect(getPriceForMaterialAndQty(testPricing, 'stainless', '10000')).toBe(1.07);
  });

  it('returns null for unknown material', () => {
    expect(getPriceForMaterialAndQty(testPricing, 'titanium', '1')).toBeNull();
  });

  it('all 3 materials have all 6 quantity tiers', () => {
    for (const mat of MATERIALS) {
      for (const qty of QUANTITIES) {
        const price = getPriceForMaterialAndQty(testPricing, mat, qty);
        expect(price).not.toBeNull();
        expect(price).toBeGreaterThan(0);
      }
    }
  });

  it('prices decrease as quantity increases for each material', () => {
    for (const mat of MATERIALS) {
      for (let i = 1; i < QUANTITIES.length; i++) {
        const prevPrice = testPricing[mat][QUANTITIES[i - 1]];
        const curPrice = testPricing[mat][QUANTITIES[i]];
        expect(curPrice).toBeLessThan(prevPrice);
      }
    }
  });

  it('formatPrice renders correctly', () => {
    expect(formatPrice(13.55)).toBe('$13.55');
    expect(formatPrice(0.46)).toBe('$0.46');
    expect(formatPrice(1)).toBe('$1.00');
  });

  it('all materials have labels', () => {
    for (const mat of MATERIALS) {
      expect(getMaterialLabel(mat)).not.toBe(mat);
    }
  });
});
