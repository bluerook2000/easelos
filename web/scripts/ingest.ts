import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import { CATEGORY_NAMES, CATEGORY_DESCRIPTIONS } from '../lib/constants';

export function createSchema(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS parts (
      part_id TEXT PRIMARY KEY,
      category TEXT NOT NULL,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      manufacturing_type TEXT NOT NULL DEFAULT 'laser_cut',
      width_mm REAL NOT NULL,
      height_mm REAL NOT NULL,
      thickness_mm REAL NOT NULL,
      width_in REAL NOT NULL,
      height_in REAL NOT NULL,
      area_sq_in REAL NOT NULL,
      hole_count INTEGER NOT NULL,
      hole_specs_json TEXT NOT NULL,
      material TEXT NOT NULL,
      material_name TEXT NOT NULL,
      weight_estimate_g REAL NOT NULL,
      complexity TEXT NOT NULL,
      size_category TEXT NOT NULL,
      pricing_json TEXT NOT NULL,
      files_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
      slug TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      part_count INTEGER NOT NULL DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category);
    CREATE INDEX IF NOT EXISTS idx_parts_material ON parts(material);
    CREATE INDEX IF NOT EXISTS idx_parts_complexity ON parts(complexity);
  `);
}

export function ingestFromDirectory(db: Database.Database, outputDir: string): number {
  const insertPart = db.prepare(`
    INSERT OR REPLACE INTO parts (
      part_id, category, name, description, manufacturing_type,
      width_mm, height_mm, thickness_mm,
      width_in, height_in, area_sq_in,
      hole_count, hole_specs_json,
      material, material_name, weight_estimate_g,
      complexity, size_category,
      pricing_json, files_json
    ) VALUES (
      @part_id, @category, @name, @description, @manufacturing_type,
      @width_mm, @height_mm, @thickness_mm,
      @width_in, @height_in, @area_sq_in,
      @hole_count, @hole_specs_json,
      @material, @material_name, @weight_estimate_g,
      @complexity, @size_category,
      @pricing_json, @files_json
    )
  `);

  const upsertCategory = db.prepare(`
    INSERT OR REPLACE INTO categories (slug, name, description, part_count)
    VALUES (@slug, @name, @description, @part_count)
  `);

  let count = 0;
  const categoryCounts: Record<string, number> = {};

  if (!fs.existsSync(outputDir)) {
    throw new Error(`Output directory not found: ${outputDir}`);
  }

  const categoryDirs = fs.readdirSync(outputDir, { withFileTypes: true })
    .filter((d) => d.isDirectory());

  const ingestAll = db.transaction(() => {
    for (const catDir of categoryDirs) {
      const catPath = path.join(outputDir, catDir.name);
      const partDirs = fs.readdirSync(catPath, { withFileTypes: true })
        .filter((d) => d.isDirectory());

      for (const partDir of partDirs) {
        const metaPath = path.join(catPath, partDir.name, 'metadata.json');
        if (!fs.existsSync(metaPath)) continue;

        const raw = fs.readFileSync(metaPath, 'utf-8');
        const meta = JSON.parse(raw);

        insertPart.run({
          part_id: meta.part_id,
          category: meta.category,
          name: meta.name,
          description: meta.description,
          manufacturing_type: meta.manufacturing_type || 'laser_cut',
          width_mm: meta.width_mm,
          height_mm: meta.height_mm,
          thickness_mm: meta.thickness_mm,
          width_in: meta.width_in,
          height_in: meta.height_in,
          area_sq_in: meta.area_sq_in,
          hole_count: meta.hole_count,
          hole_specs_json: JSON.stringify(meta.hole_specs),
          material: meta.material,
          material_name: meta.material_name,
          weight_estimate_g: meta.weight_estimate_g,
          complexity: meta.complexity,
          size_category: meta.size_category,
          pricing_json: JSON.stringify(meta.pricing),
          files_json: JSON.stringify(meta.files),
        });

        categoryCounts[meta.category] = (categoryCounts[meta.category] || 0) + 1;
        count++;
      }
    }

    // Update category summaries
    for (const [slug, partCount] of Object.entries(categoryCounts)) {
      upsertCategory.run({
        slug,
        name: CATEGORY_NAMES[slug] || slug,
        description: CATEGORY_DESCRIPTIONS[slug] || '',
        part_count: partCount,
      });
    }
  });

  ingestAll();
  return count;
}

export function buildSearchIndex(db: Database.Database, outputPath: string): void {
  const parts = db.prepare(`
    SELECT part_id, category, name, material, description, hole_specs_json
    FROM parts
  `).all() as Array<{
    part_id: string;
    category: string;
    name: string;
    material: string;
    description: string;
    hole_specs_json: string;
  }>;

  const index = parts.map((p) => {
    const holes = JSON.parse(p.hole_specs_json) as Array<{ size: string }>;
    const holeSizes = [...new Set(holes.map((h) => h.size))].join(' ');
    return {
      id: p.part_id,
      c: p.category,
      n: p.name,
      m: p.material,
      k: `${p.description} ${holeSizes}`.toLowerCase(),
    };
  });

  fs.writeFileSync(outputPath, JSON.stringify(index));
}

export function updateGrowthLog(db: Database.Database, logPath: string): void {
  const categoryCounts = db.prepare('SELECT slug, part_count FROM categories').all() as Array<{
    slug: string;
    part_count: number;
  }>;

  const totalParts = categoryCounts.reduce((sum, c) => sum + c.part_count, 0);
  const byCategory: Record<string, number> = {};
  for (const c of categoryCounts) {
    byCategory[c.slug] = c.part_count;
  }

  const entry = {
    date: new Date().toISOString().split('T')[0],
    total_parts: totalParts,
    by_category: byCategory,
  };

  let log: Array<typeof entry> = [];
  if (fs.existsSync(logPath)) {
    log = JSON.parse(fs.readFileSync(logPath, 'utf-8'));
  }

  const todayIdx = log.findIndex((e) => e.date === entry.date);
  if (todayIdx >= 0) {
    log[todayIdx] = entry;
  } else {
    log.push(entry);
  }

  fs.writeFileSync(logPath, JSON.stringify(log, null, 2));
}

// CLI entry point
const scriptPath = process.argv[1] || '';
if (scriptPath.endsWith('ingest.ts') || scriptPath.endsWith('ingest.js')) {
  const webDir = path.resolve(__dirname, '..');
  const outputDir = path.resolve(webDir, '..', 'output');
  const dataDir = path.join(webDir, 'data');
  const dbPath = path.join(dataDir, 'catalog.db');
  const searchIndexPath = path.join(webDir, 'public', 'search-index.json');
  const growthLogPath = path.join(dataDir, 'growth-log.json');

  fs.mkdirSync(dataDir, { recursive: true });
  fs.mkdirSync(path.join(webDir, 'public'), { recursive: true });

  // Create symlink for static assets
  const symlinkPath = path.join(webDir, 'public', 'parts');
  if (!fs.existsSync(symlinkPath)) {
    fs.symlinkSync(outputDir, symlinkPath);
    console.log(`Created symlink: ${symlinkPath} -> ${outputDir}`);
  }

  // Delete and recreate database
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
  }

  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');

  createSchema(db);
  const count = ingestFromDirectory(db, outputDir);
  console.log(`Ingested ${count} parts into ${dbPath}`);

  buildSearchIndex(db, searchIndexPath);
  console.log(`Built search index at ${searchIndexPath}`);

  updateGrowthLog(db, growthLogPath);
  console.log(`Updated growth log at ${growthLogPath}`);

  db.close();
}
