import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import Database from 'better-sqlite3';
import {
  createVendorSchema,
  createVendor,
  getVendorByEmail,
  getVendorById,
  getVendorInterests,
  createVendorInterest,
  getAllVendors,
  getVendorDb,
} from '../lib/vendor-db';

describe('Vendor database', () => {
  let tmpDir: string;
  let db: Database.Database;

  beforeAll(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'easelos-vendortest-'));
    const dbPath = path.join(tmpDir, 'vendor.db');
    db = new Database(dbPath);
    db.pragma('journal_mode = WAL');
    createVendorSchema(db);
  });

  afterAll(() => {
    db.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('creates vendor schema with all tables', () => {
    const tables = db.prepare(
      "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).all() as Array<{ name: string }>;
    const tableNames = tables.map((t) => t.name);
    expect(tableNames).toContain('vendors');
    expect(tableNames).toContain('vendor_machines');
    expect(tableNames).toContain('vendor_materials');
    expect(tableNames).toContain('vendor_certifications');
    expect(tableNames).toContain('vendor_interests');
    expect(tableNames).toContain('nextauth_users');
  });

  it('creates a vendor with full profile', () => {
    const id = createVendor(db, {
      company_name: 'Acme Manufacturing',
      contact_name: 'John Smith',
      email: 'john@acme.com',
      phone: '555-0100',
      website: 'https://acme.com',
      city: 'San Jose',
      state: 'CA',
      country: 'US',
      capacity: 'medium',
      lead_time: '1-2 weeks',
      machines: [
        { machine_type: 'CNC Mill', make_model: 'Haas VF-2', max_part_size_mm: '300x200x150' },
        { machine_type: 'Laser CO2', make_model: 'Epilog Fusion Pro', max_part_size_mm: '1016x711' },
      ],
      materials: ['aluminum', 'steel', 'stainless'],
      certifications: ['ISO 9001', 'AS9100D'],
    });
    expect(id).toBeGreaterThan(0);
  });

  it('retrieves vendor by email', () => {
    const vendor = getVendorByEmail(db, 'john@acme.com');
    expect(vendor).not.toBeNull();
    expect(vendor!.company_name).toBe('Acme Manufacturing');
    expect(vendor!.machines).toHaveLength(2);
    expect(vendor!.materials).toEqual(['aluminum', 'stainless', 'steel']);
    expect(vendor!.certifications).toEqual(['AS9100D', 'ISO 9001']);
  });

  it('retrieves vendor by ID', () => {
    const byEmail = getVendorByEmail(db, 'john@acme.com');
    const vendor = getVendorById(db, byEmail!.id);
    expect(vendor).not.toBeNull();
    expect(vendor!.email).toBe('john@acme.com');
  });

  it('re-registration updates existing vendor', () => {
    createVendor(db, {
      company_name: 'Acme Manufacturing LLC',
      contact_name: 'John Smith',
      email: 'john@acme.com',
      phone: '555-0101',
      website: 'https://acme.com',
      city: 'San Jose',
      state: 'CA',
      country: 'US',
      capacity: 'high',
      lead_time: '3-7 days',
      machines: [
        { machine_type: 'CNC Mill', make_model: 'Haas VF-2', max_part_size_mm: '300x200x150' },
      ],
      materials: ['aluminum', 'steel'],
      certifications: ['ISO 9001'],
    });
    const vendor = getVendorByEmail(db, 'john@acme.com');
    expect(vendor!.company_name).toBe('Acme Manufacturing LLC');
    expect(vendor!.capacity).toBe('high');
    expect(vendor!.machines).toHaveLength(1);
    expect(vendor!.materials).toEqual(['aluminum', 'steel']);
  });

  it('creates vendor interest for a part', () => {
    const vendor = getVendorByEmail(db, 'john@acme.com');
    createVendorInterest(db, vendor!.id, 'bracket-flat-30x20-2xM3-1.5mm-aluminum', 'mounting_bracket');
    const interests = getVendorInterests(db, vendor!.id);
    expect(interests).toHaveLength(1);
    expect(interests[0].part_id).toBe('bracket-flat-30x20-2xM3-1.5mm-aluminum');
    expect(interests[0].category).toBe('mounting_bracket');
  });

  it('duplicate interest is idempotent', () => {
    const vendor = getVendorByEmail(db, 'john@acme.com');
    createVendorInterest(db, vendor!.id, 'bracket-flat-30x20-2xM3-1.5mm-aluminum', 'mounting_bracket');
    const interests = getVendorInterests(db, vendor!.id);
    expect(interests).toHaveLength(1);
  });

  it('creates a second vendor for filtering tests', () => {
    createVendor(db, {
      company_name: 'Beta Shop',
      contact_name: 'Jane Doe',
      email: 'jane@betashop.com',
      phone: '555-0200',
      website: '',
      city: 'Austin',
      state: 'TX',
      country: 'US',
      capacity: 'prototype',
      lead_time: '1-3 days',
      machines: [
        { machine_type: '3D Printer FDM', make_model: 'Prusa MK4', max_part_size_mm: '250x210x210' },
      ],
      materials: ['nylon', 'acrylic'],
      certifications: [],
    });
    const all = getAllVendors(db, {});
    expect(all).toHaveLength(2);
  });

  it('filters vendors by material', () => {
    const filtered = getAllVendors(db, { material: 'aluminum' });
    expect(filtered).toHaveLength(1);
    expect(filtered[0].company_name).toBe('Acme Manufacturing LLC');
  });

  it('filters vendors by machine type', () => {
    const filtered = getAllVendors(db, { machine_type: '3D Printer FDM' });
    expect(filtered).toHaveLength(1);
    expect(filtered[0].company_name).toBe('Beta Shop');
  });

  it('filters vendors by certification', () => {
    const filtered = getAllVendors(db, { certification: 'ISO 9001' });
    expect(filtered).toHaveLength(1);
  });

  it('filters vendors by capacity', () => {
    const filtered = getAllVendors(db, { capacity: 'prototype' });
    expect(filtered).toHaveLength(1);
    expect(filtered[0].company_name).toBe('Beta Shop');
  });

  it('rejects vendor with missing required fields', () => {
    expect(() => createVendor(db, {
      company_name: '',
      contact_name: 'Test',
      email: 'test@test.com',
      phone: '',
      website: '',
      city: '',
      state: '',
      country: '',
      capacity: 'low',
      lead_time: '1-3 days',
      machines: [],
      materials: [],
      certifications: [],
    })).toThrow('company_name is required');
  });

  it('rejects vendor with invalid email', () => {
    expect(() => createVendor(db, {
      company_name: 'Test Co',
      contact_name: 'Test',
      email: 'not-an-email',
      phone: '',
      website: '',
      city: '',
      state: '',
      country: '',
      capacity: 'low',
      lead_time: '1-3 days',
      machines: [],
      materials: [],
      certifications: [],
    })).toThrow('Invalid email');
  });

  it('handles very long company name', () => {
    const longName = 'A'.repeat(300);
    expect(() => createVendor(db, {
      company_name: longName,
      contact_name: 'Test',
      email: 'long@test.com',
      phone: '',
      website: '',
      city: '',
      state: '',
      country: '',
      capacity: 'low',
      lead_time: '1-3 days',
      machines: [],
      materials: [],
      certifications: [],
    })).toThrow('company_name exceeds 255 characters');
  });
});
