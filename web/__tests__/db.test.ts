import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import Database from 'better-sqlite3';
import { createSchema, ingestFromDirectory } from '../scripts/ingest';
import {
  getAllCategories,
  getPartsByCategory,
  getPartById,
  getPartsByMaterial,
  getPartCount,
} from '../lib/db';

describe('Database queries', () => {
  let tmpDir: string;
  let dbPath: string;
  let db: Database.Database;

  beforeAll(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'easelos-dbtest-'));
    dbPath = path.join(tmpDir, 'test.db');

    const parts = [
      { part_id: 'bracket-1', category: 'mounting_bracket', name: 'Bracket A', material: 'aluminum', width_mm: 30, height_mm: 20 },
      { part_id: 'bracket-2', category: 'mounting_bracket', name: 'Bracket B', material: 'steel', width_mm: 50, height_mm: 30 },
      { part_id: 'motor-1', category: 'motor_mount', name: 'Motor Mount A', material: 'aluminum', width_mm: 42, height_mm: 42 },
    ];

    for (const p of parts) {
      const dir = path.join(tmpDir, 'output', p.category, p.part_id);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, 'metadata.json'), JSON.stringify({
        ...p,
        description: `Test ${p.name}`,
        manufacturing_type: 'laser_cut',
        thickness_mm: 1.6, width_in: 1.0, height_in: 1.0, area_sq_in: 1.0,
        hole_count: 2, hole_specs: [],
        material_name: p.material, weight_estimate_g: 1.0,
        complexity: 'simple', size_category: 'small',
        pricing: { aluminum: { '1': 12.88 }, steel: { '1': 12.88 }, stainless: { '1': 12.88 } },
        files: { step: 'part.step', svg: 'profile.svg', dxf: 'profile.dxf', png: 'thumbnail.png', metadata: 'metadata.json' },
      }));
    }

    db = new Database(dbPath);
    db.pragma('journal_mode = WAL');
    createSchema(db);
    ingestFromDirectory(db, path.join(tmpDir, 'output'));
  });

  afterAll(() => {
    db.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('getAllCategories returns all categories with counts', () => {
    const categories = getAllCategories(db);
    expect(categories).toHaveLength(2);
    const bracket = categories.find((c) => c.slug === 'mounting_bracket');
    expect(bracket?.part_count).toBe(2);
  });

  it('getPartsByCategory returns parts sorted by name', () => {
    const parts = getPartsByCategory(db, 'mounting_bracket');
    expect(parts).toHaveLength(2);
    expect(parts[0].name).toBe('Bracket A');
    expect(parts[1].name).toBe('Bracket B');
  });

  it('getPartsByCategory with sort by width_mm desc', () => {
    const parts = getPartsByCategory(db, 'mounting_bracket', 'width_mm', 'desc');
    expect(parts[0].part_id).toBe('bracket-2');
  });

  it('getPartById returns full part with parsed JSON fields', () => {
    const part = getPartById(db, 'bracket-1');
    expect(part).not.toBeNull();
    expect(part!.name).toBe('Bracket A');
    expect(part!.pricing).toBeDefined();
    expect(part!.pricing.aluminum['1']).toBe(12.88);
  });

  it('getPartById returns null for nonexistent part', () => {
    const part = getPartById(db, 'nonexistent');
    expect(part).toBeNull();
  });

  it('getPartsByMaterial returns filtered parts', () => {
    const parts = getPartsByMaterial(db, 'aluminum');
    expect(parts).toHaveLength(2);
  });

  it('getPartCount returns total parts', () => {
    const count = getPartCount(db);
    expect(count).toBe(3);
  });
});
