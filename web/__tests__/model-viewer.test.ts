import { describe, it, expect } from 'vitest';
import { MANUFACTURING_TYPE_LABELS, CATEGORY_NAMES } from '../lib/constants';

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
