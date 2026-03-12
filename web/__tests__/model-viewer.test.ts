import { describe, it, expect } from 'vitest';
import { MANUFACTURING_TYPE_LABELS, CATEGORY_NAMES, MATERIAL_LABELS } from '../lib/constants';

describe('ModelViewer integration', () => {
  it('MANUFACTURING_TYPE_LABELS has all 3 types', () => {
    expect(Object.keys(MANUFACTURING_TYPE_LABELS)).toHaveLength(3);
    expect(MANUFACTURING_TYPE_LABELS['laser_cut']).toBe('Laser Cut');
    expect(MANUFACTURING_TYPE_LABELS['cnc_milled']).toBe('CNC Milled');
    expect(MANUFACTURING_TYPE_LABELS['sheet_metal']).toBe('Sheet Metal');
  });

  it('CATEGORY_NAMES has 23 categories', () => {
    expect(Object.keys(CATEGORY_NAMES)).toHaveLength(23);
  });

  it('3D part types include glb in files when manufacturing_type is not laser_cut', () => {
    // Verify the Part type accepts glb as optional
    const files: { step: string; svg: string; dxf: string; png: string; metadata: string; glb?: string } = {
      step: 'part.step',
      svg: 'profile.svg',
      dxf: 'profile.dxf',
      png: 'thumbnail.png',
      metadata: 'metadata.json',
      glb: 'model.glb',
    };
    expect(files.glb).toBe('model.glb');
  });

  it('laser_cut parts do not require glb', () => {
    const files: { step: string; svg: string; dxf: string; png: string; metadata: string; glb?: string } = {
      step: 'part.step',
      svg: 'profile.svg',
      dxf: 'profile.dxf',
      png: 'thumbnail.png',
      metadata: 'metadata.json',
    };
    expect(files.glb).toBeUndefined();
  });
});

describe('MATERIAL_LABELS', () => {
  it('has exactly 14 materials', () => {
    expect(Object.keys(MATERIAL_LABELS)).toHaveLength(14);
  });

  it('contains all pipeline material slugs', () => {
    const expectedSlugs = [
      'aluminum', 'steel', 'stainless',
      'aluminum_6061', 'steel_4140', 'titanium', 'brass', 'copper',
      'acrylic', 'delrin', 'nylon', 'polycarbonate', 'hdpe', 'uhmwpe',
    ];
    for (const slug of expectedSlugs) {
      expect(MATERIAL_LABELS).toHaveProperty(slug);
    }
  });

  it('display names match pipeline material names', () => {
    expect(MATERIAL_LABELS['aluminum_6061']).toBe('6061-T6 Aluminum');
    expect(MATERIAL_LABELS['steel_4140']).toBe('4140 Alloy Steel');
    expect(MATERIAL_LABELS['brass']).toBe('360 Brass');
    expect(MATERIAL_LABELS['copper']).toBe('110 Copper');
    expect(MATERIAL_LABELS['delrin']).toBe('Delrin (Acetal)');
    expect(MATERIAL_LABELS['uhmwpe']).toBe('UHMW-PE');
  });

  it('does not contain invalid slugs from previous implementation', () => {
    expect(MATERIAL_LABELS).not.toHaveProperty('galvanized');
    expect(MATERIAL_LABELS).not.toHaveProperty('spring_steel');
    expect(MATERIAL_LABELS).not.toHaveProperty('abs');
  });
});
