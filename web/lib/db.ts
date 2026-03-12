import Database from 'better-sqlite3';
import path from 'path';
import type { Part, CategorySummary, PartPricing, HoleSpec } from './types';

const DB_PATH = path.join(process.cwd(), 'data', 'catalog.db');

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true });
    _db.pragma('journal_mode = WAL');
  }
  return _db;
}

export function openDb(dbPath: string, readonly = true): Database.Database {
  const db = new Database(dbPath, { readonly });
  db.pragma('journal_mode = WAL');
  return db;
}

interface PartRow {
  part_id: string;
  category: string;
  name: string;
  description: string;
  width_mm: number;
  height_mm: number;
  thickness_mm: number;
  width_in: number;
  height_in: number;
  area_sq_in: number;
  hole_count: number;
  hole_specs_json: string;
  material: string;
  material_name: string;
  weight_estimate_g: number;
  complexity: string;
  size_category: string;
  pricing_json: string;
  files_json: string;
}

function rowToPart(row: PartRow): Part {
  return {
    part_id: row.part_id,
    category: row.category,
    name: row.name,
    description: row.description,
    width_mm: row.width_mm,
    height_mm: row.height_mm,
    thickness_mm: row.thickness_mm,
    width_in: row.width_in,
    height_in: row.height_in,
    area_sq_in: row.area_sq_in,
    hole_count: row.hole_count,
    hole_specs: JSON.parse(row.hole_specs_json) as HoleSpec[],
    material: row.material,
    material_name: row.material_name,
    weight_estimate_g: row.weight_estimate_g,
    complexity: row.complexity,
    size_category: row.size_category,
    pricing: JSON.parse(row.pricing_json) as PartPricing,
    files: JSON.parse(row.files_json),
  };
}

const VALID_SORT_COLUMNS = ['name', 'width_mm', 'height_mm', 'area_sq_in', 'weight_estimate_g', 'hole_count'] as const;
type SortColumn = (typeof VALID_SORT_COLUMNS)[number];

export function getAllCategories(db: Database.Database): CategorySummary[] {
  return db.prepare('SELECT slug, name, description, part_count FROM categories ORDER BY name').all() as CategorySummary[];
}

export function getPartsByCategory(
  db: Database.Database,
  category: string,
  sortBy: SortColumn = 'name',
  sortDir: 'asc' | 'desc' = 'asc',
): Part[] {
  if (!VALID_SORT_COLUMNS.includes(sortBy)) sortBy = 'name';
  const dir = sortDir === 'desc' ? 'DESC' : 'ASC';
  const rows = db.prepare(
    `SELECT * FROM parts WHERE category = ? ORDER BY ${sortBy} ${dir}`
  ).all(category) as PartRow[];
  return rows.map(rowToPart);
}

export function getPartById(db: Database.Database, partId: string): Part | null {
  const row = db.prepare('SELECT * FROM parts WHERE part_id = ?').get(partId) as PartRow | undefined;
  if (!row) return null;
  return rowToPart(row);
}

export function getPartsByMaterial(db: Database.Database, material: string): Part[] {
  const rows = db.prepare('SELECT * FROM parts WHERE material = ? ORDER BY name').all(material) as PartRow[];
  return rows.map(rowToPart);
}

export function getPartCount(db: Database.Database): number {
  const row = db.prepare('SELECT COUNT(*) as count FROM parts').get() as { count: number };
  return row.count;
}

export function getRelatedParts(db: Database.Database, part: Part, limit = 6): Part[] {
  const rows = db.prepare(
    `SELECT * FROM parts WHERE category = ? AND part_id != ? ORDER BY ABS(area_sq_in - ?) ASC LIMIT ?`
  ).all(part.category, part.part_id, part.area_sq_in, limit) as PartRow[];
  return rows.map(rowToPart);
}
