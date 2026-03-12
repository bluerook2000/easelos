import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import Database from 'better-sqlite3';
import { createVendorSchema, createVendor } from '../lib/vendor-db';

let tmpDir: string;
let testDb: Database.Database;

vi.mock('../lib/vendor-db', async (importOriginal) => {
  const original = await importOriginal() as any;
  return {
    ...original,
    getVendorDb: () => testDb,
  };
});

vi.mock('next-auth', () => ({
  default: vi.fn(),
  getServerSession: vi.fn(),
}));

vi.mock('../lib/auth', () => ({
  authOptions: {},
}));

import { getServerSession } from 'next-auth';
const mockedGetSession = vi.mocked(getServerSession);

import { GET as adminVendorsHandler } from '../app/api/admin/vendors/route';

describe('Admin API routes', () => {
  beforeAll(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'easelos-admintest-'));
    const dbPath = path.join(tmpDir, 'vendor.db');
    testDb = new Database(dbPath);
    testDb.pragma('journal_mode = WAL');
    createVendorSchema(testDb);
    // Seed a vendor for list tests
    createVendor(testDb, {
      company_name: 'Admin Test Co',
      contact_name: 'Admin Tester',
      email: 'admin-test@test.com',
      phone: '555-9999',
      website: '',
      city: 'NYC',
      state: 'NY',
      country: 'US',
      capacity: 'medium',
      lead_time: '1-2 weeks',
      machines: [{ machine_type: 'CNC Mill', make_model: 'Test', max_part_size_mm: '200x200' }],
      materials: ['aluminum'],
      certifications: [],
    });
  });

  afterAll(() => {
    testDb.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('GET /api/admin/vendors without auth returns 401', async () => {
    mockedGetSession.mockResolvedValue(null);
    const req = new Request('http://localhost:3000/api/admin/vendors');
    const res = await adminVendorsHandler(req);
    expect(res.status).toBe(401);
  });

  it('GET /api/admin/vendors as non-admin returns 403', async () => {
    process.env.ADMIN_EMAILS = 'admin@easelos.com';
    mockedGetSession.mockResolvedValue({ user: { email: 'admin-test@test.com' } });
    const req = new Request('http://localhost:3000/api/admin/vendors');
    const res = await adminVendorsHandler(req);
    expect(res.status).toBe(403);
    delete process.env.ADMIN_EMAILS;
  });

  it('GET /api/admin/vendors as admin returns vendor list', async () => {
    process.env.ADMIN_EMAILS = 'admin@easelos.com';
    mockedGetSession.mockResolvedValue({ user: { email: 'admin@easelos.com' } });
    const req = new Request('http://localhost:3000/api/admin/vendors');
    const res = await adminVendorsHandler(req);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.vendors).toBeDefined();
    expect(data.total).toBeGreaterThanOrEqual(1);
    delete process.env.ADMIN_EMAILS;
  });
});
