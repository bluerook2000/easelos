import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import Database from 'better-sqlite3';

import { ingestFromDirectory, createSchema } from '../scripts/ingest';

describe('Data ingestion', () => {
  let tmpDir: string;
  let dbPath: string;

  beforeAll(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'easelos-test-'));
    dbPath = path.join(tmpDir, 'test-catalog.db');

    const part1Dir = path.join(tmpDir, 'output', 'mounting_bracket', 'bracket-flat-30x20x1.6-4xM5-aluminum');
    const part2Dir = path.join(tmpDir, 'output', 'motor_mount', 'motor_mount-nema17-42x42x1.52-4xM3-steel');
    fs.mkdirSync(part1Dir, { recursive: true });
    fs.mkdirSync(part2Dir, { recursive: true });

    const meta1 = {
      part_id: 'bracket-flat-30x20x1.6-4xM5-aluminum',
      category: 'mounting_bracket',
      name: '5052-H32 Aluminum Flat Bracket 30x20mm 4xM5',
      description: 'Laser-cut flat mounting bracket.',
      manufacturing_type: 'laser_cut',
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

    const meta2 = {
      part_id: 'motor_mount-nema17-42x42x1.52-4xM3-steel',
      category: 'motor_mount',
      name: 'A1011 Steel NEMA 17 Motor Mount 42x42mm',
      description: 'Laser-cut steel motor mount plate.',
      manufacturing_type: 'laser_cut',
      width_mm: 42, height_mm: 42, thickness_mm: 1.52,
      width_in: 1.65, height_in: 1.65, area_sq_in: 2.72,
      hole_count: 4,
      hole_specs: [{ size: 'M3', diameter_mm: 3.4, x_mm: -15.5, y_mm: -15.5 }],
      material: 'steel', material_name: 'A1011 Hot Rolled Carbon Steel',
      weight_estimate_g: 16.8, complexity: 'moderate', size_category: 'small',
      pricing: {
        aluminum: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
        steel: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
        stainless: { '1': 13.55, '10': 3.02, '100': 1.01, '500': 0.81, '1000': 0.71, '10000': 0.46 },
      },
      files: { step: 'part.step', svg: 'profile.svg', dxf: 'profile.dxf', png: 'thumbnail.png', metadata: 'metadata.json' },
    };

    fs.writeFileSync(path.join(part1Dir, 'metadata.json'), JSON.stringify(meta1));
    fs.writeFileSync(path.join(part2Dir, 'metadata.json'), JSON.stringify(meta2));
  });

  afterAll(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('creates schema with parts and categories tables', () => {
    const db = new Database(dbPath);
    createSchema(db);
    const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all() as { name: string }[];
    const tableNames = tables.map((t) => t.name);
    expect(tableNames).toContain('parts');
    expect(tableNames).toContain('categories');
    db.close();
  });

  it('ingests metadata.json files into SQLite', () => {
    const db = new Database(dbPath);
    createSchema(db);
    const count = ingestFromDirectory(db, path.join(tmpDir, 'output'));
    expect(count).toBe(2);

    const parts = db.prepare('SELECT * FROM parts').all();
    expect(parts).toHaveLength(2);

    const categories = db.prepare('SELECT * FROM categories').all();
    expect(categories).toHaveLength(2);
    db.close();
  });

  it('handles re-ingestion idempotently (INSERT OR REPLACE)', () => {
    const db = new Database(dbPath);
    createSchema(db);
    ingestFromDirectory(db, path.join(tmpDir, 'output'));
    const count2 = ingestFromDirectory(db, path.join(tmpDir, 'output'));
    expect(count2).toBe(2);

    const parts = db.prepare('SELECT * FROM parts').all();
    expect(parts).toHaveLength(2);
    db.close();
  });

  it('stores manufacturing_type column', () => {
    const db = new Database(dbPath);
    createSchema(db);
    ingestFromDirectory(db, path.join(tmpDir, 'output'));
    const row = db.prepare('SELECT manufacturing_type FROM parts WHERE part_id = ?').get('bracket-flat-30x20x1.6-4xM5-aluminum') as { manufacturing_type: string };
    expect(row.manufacturing_type).toBe('laser_cut');
    db.close();
  });

  it('schema has manufacturing_type column', () => {
    const db = new Database(dbPath);
    createSchema(db);
    const cols = db.prepare("PRAGMA table_info('parts')").all() as Array<{ name: string }>;
    const colNames = cols.map((c) => c.name);
    expect(colNames).toContain('manufacturing_type');
    db.close();
  });

  it('stores pricing as JSON string', () => {
    const db = new Database(dbPath);
    createSchema(db);
    ingestFromDirectory(db, path.join(tmpDir, 'output'));
    const row = db.prepare('SELECT pricing_json FROM parts WHERE part_id = ?').get('bracket-flat-30x20x1.6-4xM5-aluminum') as { pricing_json: string };
    const pricing = JSON.parse(row.pricing_json);
    expect(pricing.aluminum['1']).toBe(13.55);
    expect(pricing.steel['10000']).toBe(0.46);
    db.close();
  });
});
