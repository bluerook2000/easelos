import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

const VENDOR_DB_PATH = path.join(process.cwd(), 'data', 'vendor.db');

let _vendorDb: Database.Database | null = null;

export function getVendorDb(): Database.Database {
  if (!_vendorDb) {
    // Ensure the data/ directory exists (it may not on a fresh clone before ingest runs)
    const dataDir = path.dirname(VENDOR_DB_PATH);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    _vendorDb = new Database(VENDOR_DB_PATH);
    _vendorDb.pragma('journal_mode = WAL');
    createVendorSchema(_vendorDb);
  }
  return _vendorDb;
}

export function createVendorSchema(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS vendors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company_name TEXT NOT NULL,
      contact_name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      phone TEXT NOT NULL DEFAULT '',
      website TEXT NOT NULL DEFAULT '',
      city TEXT NOT NULL DEFAULT '',
      state TEXT NOT NULL DEFAULT '',
      country TEXT NOT NULL DEFAULT '',
      capacity TEXT NOT NULL DEFAULT 'low',
      lead_time TEXT NOT NULL DEFAULT '1-2 weeks',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS vendor_machines (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
      machine_type TEXT NOT NULL,
      make_model TEXT NOT NULL DEFAULT '',
      max_part_size_mm TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS vendor_materials (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
      material TEXT NOT NULL,
      UNIQUE(vendor_id, material)
    );

    CREATE TABLE IF NOT EXISTS vendor_certifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
      certification TEXT NOT NULL,
      UNIQUE(vendor_id, certification)
    );

    CREATE TABLE IF NOT EXISTS vendor_interests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
      part_id TEXT NOT NULL,
      category TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      UNIQUE(vendor_id, part_id)
    );

    CREATE TABLE IF NOT EXISTS verification_tokens (
      identifier TEXT NOT NULL,
      token TEXT NOT NULL UNIQUE,
      expires TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_vt_token ON verification_tokens(token);

    CREATE TABLE IF NOT EXISTS nextauth_users (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE,
      email_verified TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_nau_email ON nextauth_users(email);

    CREATE INDEX IF NOT EXISTS idx_vendor_email ON vendors(email);
    CREATE INDEX IF NOT EXISTS idx_vendor_machines_vendor ON vendor_machines(vendor_id);
    CREATE INDEX IF NOT EXISTS idx_vendor_materials_vendor ON vendor_materials(vendor_id);
    CREATE INDEX IF NOT EXISTS idx_vendor_certs_vendor ON vendor_certifications(vendor_id);
    CREATE INDEX IF NOT EXISTS idx_vendor_interests_vendor ON vendor_interests(vendor_id);
    CREATE INDEX IF NOT EXISTS idx_vendor_interests_part ON vendor_interests(part_id);
  `);
}

export interface VendorMachineInput {
  machine_type: string;
  make_model: string;
  max_part_size_mm: string;
}

export interface VendorInput {
  company_name: string;
  contact_name: string;
  email: string;
  phone: string;
  website: string;
  city: string;
  state: string;
  country: string;
  capacity: string;
  lead_time: string;
  machines: VendorMachineInput[];
  materials: string[];
  certifications: string[];
}

export interface VendorMachine {
  machine_type: string;
  make_model: string;
  max_part_size_mm: string;
}

export interface Vendor {
  id: number;
  company_name: string;
  contact_name: string;
  email: string;
  phone: string;
  website: string;
  city: string;
  state: string;
  country: string;
  capacity: string;
  lead_time: string;
  created_at: string;
  updated_at: string;
  machines: VendorMachine[];
  materials: string[];
  certifications: string[];
}

export interface VendorInterest {
  part_id: string;
  category: string;
  created_at: string;
}

function validateVendorInput(input: VendorInput): void {
  if (!input.company_name || input.company_name.trim() === '') {
    throw new Error('company_name is required');
  }
  if (input.company_name.length > 255) {
    throw new Error('company_name exceeds 255 characters');
  }
  if (!input.contact_name || input.contact_name.trim() === '') {
    throw new Error('contact_name is required');
  }
  if (!input.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) {
    throw new Error('Invalid email');
  }
}

export function createVendor(db: Database.Database, input: VendorInput): number {
  validateVendorInput(input);

  const upsert = db.transaction(() => {
    // Upsert vendor core record
    const existingVendor = db.prepare('SELECT id FROM vendors WHERE email = ?').get(input.email) as { id: number } | undefined;

    let vendorId: number;
    if (existingVendor) {
      vendorId = existingVendor.id;
      db.prepare(`
        UPDATE vendors SET
          company_name = ?, contact_name = ?, phone = ?, website = ?,
          city = ?, state = ?, country = ?, capacity = ?, lead_time = ?,
          updated_at = datetime('now')
        WHERE id = ?
      `).run(
        input.company_name, input.contact_name, input.phone, input.website,
        input.city, input.state, input.country, input.capacity, input.lead_time,
        vendorId
      );

      // Clear old related data for re-registration
      db.prepare('DELETE FROM vendor_machines WHERE vendor_id = ?').run(vendorId);
      db.prepare('DELETE FROM vendor_materials WHERE vendor_id = ?').run(vendorId);
      db.prepare('DELETE FROM vendor_certifications WHERE vendor_id = ?').run(vendorId);
    } else {
      const result = db.prepare(`
        INSERT INTO vendors (company_name, contact_name, email, phone, website, city, state, country, capacity, lead_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        input.company_name, input.contact_name, input.email, input.phone, input.website,
        input.city, input.state, input.country, input.capacity, input.lead_time
      );
      vendorId = Number(result.lastInsertRowid);
    }

    // Insert machines
    const insertMachine = db.prepare(
      'INSERT INTO vendor_machines (vendor_id, machine_type, make_model, max_part_size_mm) VALUES (?, ?, ?, ?)'
    );
    for (const m of input.machines) {
      insertMachine.run(vendorId, m.machine_type, m.make_model, m.max_part_size_mm);
    }

    // Insert materials
    const insertMaterial = db.prepare(
      'INSERT INTO vendor_materials (vendor_id, material) VALUES (?, ?)'
    );
    for (const mat of input.materials) {
      insertMaterial.run(vendorId, mat);
    }

    // Insert certifications
    const insertCert = db.prepare(
      'INSERT INTO vendor_certifications (vendor_id, certification) VALUES (?, ?)'
    );
    for (const cert of input.certifications) {
      insertCert.run(vendorId, cert);
    }

    return vendorId;
  });

  return upsert();
}

function hydrateVendor(db: Database.Database, row: any): Vendor {
  const machines = db.prepare(
    'SELECT machine_type, make_model, max_part_size_mm FROM vendor_machines WHERE vendor_id = ? ORDER BY id'
  ).all(row.id) as VendorMachine[];

  const materials = db.prepare(
    'SELECT material FROM vendor_materials WHERE vendor_id = ? ORDER BY material'
  ).all(row.id) as Array<{ material: string }>;

  const certifications = db.prepare(
    'SELECT certification FROM vendor_certifications WHERE vendor_id = ? ORDER BY certification'
  ).all(row.id) as Array<{ certification: string }>;

  return {
    id: row.id,
    company_name: row.company_name,
    contact_name: row.contact_name,
    email: row.email,
    phone: row.phone,
    website: row.website,
    city: row.city,
    state: row.state,
    country: row.country,
    capacity: row.capacity,
    lead_time: row.lead_time,
    created_at: row.created_at,
    updated_at: row.updated_at,
    machines,
    materials: materials.map((m) => m.material),
    certifications: certifications.map((c) => c.certification),
  };
}

export function getVendorByEmail(db: Database.Database, email: string): Vendor | null {
  const row = db.prepare('SELECT * FROM vendors WHERE email = ?').get(email);
  if (!row) return null;
  return hydrateVendor(db, row);
}

export function getVendorById(db: Database.Database, id: number): Vendor | null {
  const row = db.prepare('SELECT * FROM vendors WHERE id = ?').get(id);
  if (!row) return null;
  return hydrateVendor(db, row);
}

export interface VendorFilter {
  material?: string;
  machine_type?: string;
  certification?: string;
  capacity?: string;
}

export function getAllVendors(db: Database.Database, filter: VendorFilter): Vendor[] {
  let query = 'SELECT DISTINCT v.* FROM vendors v';
  const joins: string[] = [];
  const conditions: string[] = [];
  const params: string[] = [];

  if (filter.material) {
    joins.push('JOIN vendor_materials vm ON v.id = vm.vendor_id');
    conditions.push('vm.material = ?');
    params.push(filter.material);
  }
  if (filter.machine_type) {
    joins.push('JOIN vendor_machines vmach ON v.id = vmach.vendor_id');
    conditions.push('vmach.machine_type = ?');
    params.push(filter.machine_type);
  }
  if (filter.certification) {
    joins.push('JOIN vendor_certifications vc ON v.id = vc.vendor_id');
    conditions.push('vc.certification = ?');
    params.push(filter.certification);
  }
  if (filter.capacity) {
    conditions.push('v.capacity = ?');
    params.push(filter.capacity);
  }

  query += ' ' + joins.join(' ');
  if (conditions.length > 0) {
    query += ' WHERE ' + conditions.join(' AND ');
  }
  query += ' ORDER BY v.created_at DESC';

  const rows = db.prepare(query).all(...params) as any[];
  return rows.map((row) => hydrateVendor(db, row));
}

export function createVendorInterest(db: Database.Database, vendorId: number, partId: string, category: string = ''): void {
  db.prepare(
    'INSERT OR IGNORE INTO vendor_interests (vendor_id, part_id, category) VALUES (?, ?, ?)'
  ).run(vendorId, partId, category);
}

export function getVendorInterests(db: Database.Database, vendorId: number): VendorInterest[] {
  return db.prepare(
    'SELECT part_id, category, created_at FROM vendor_interests WHERE vendor_id = ? ORDER BY created_at DESC'
  ).all(vendorId) as VendorInterest[];
}
