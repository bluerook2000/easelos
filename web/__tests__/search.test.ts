import { describe, it, expect } from 'vitest';
import { searchParts, type SearchEntry } from '../lib/search';

const testIndex: SearchEntry[] = [
  { id: 'bracket-1', c: 'mounting_bracket', n: 'Aluminum Flat Bracket 30x20mm 4xM5', m: 'aluminum', k: 'flat mounting bracket m5 laser-cut' },
  { id: 'motor-1', c: 'motor_mount', n: 'Steel NEMA 17 Motor Mount', m: 'steel', k: 'nema 17 motor mount plate m3' },
  { id: 'gusset-1', c: 'gusset_plate', n: 'Stainless Corner Gusset 50x50mm', m: 'stainless', k: 'corner gusset reinforcement m4' },
];

describe('Client-side search', () => {
  it('matches by part name', () => {
    const results = searchParts(testIndex, 'bracket');
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('bracket-1');
  });

  it('matches by material', () => {
    const results = searchParts(testIndex, 'steel');
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('motor-1');
  });

  it('matches by keywords (hole size)', () => {
    const results = searchParts(testIndex, 'M5');
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('bracket-1');
  });

  it('matches by category', () => {
    const results = searchParts(testIndex, 'motor_mount');
    expect(results).toHaveLength(1);
  });

  it('multi-word query requires all terms', () => {
    const results = searchParts(testIndex, 'aluminum bracket');
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('bracket-1');
  });

  it('returns empty for no match', () => {
    const results = searchParts(testIndex, 'titanium');
    expect(results).toHaveLength(0);
  });

  it('is case-insensitive', () => {
    const results = searchParts(testIndex, 'NEMA');
    expect(results).toHaveLength(1);
  });

  it('limits results', () => {
    const results = searchParts(testIndex, '', 2);
    expect(results.length).toBeLessThanOrEqual(2);
  });
});
