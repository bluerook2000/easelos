import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import Database from 'better-sqlite3';
import { createVendorSchema, getVendorByEmail, getVendorInterests } from '../lib/vendor-db';

// We test the handler logic by importing and calling the route handler functions directly.
// The route handlers need getServerSession, which we mock.

let tmpDir: string;
let testDb: Database.Database;

// Mock vendor-db to use our test database
vi.mock('../lib/vendor-db', async (importOriginal) => {
  const original = await importOriginal() as any;
  return {
    ...original,
    getVendorDb: () => testDb,
  };
});

// Mock next-auth to return a controlled session
vi.mock('next-auth', () => ({
  default: vi.fn(),
  getServerSession: vi.fn(),
}));

vi.mock('../lib/auth', () => ({
  authOptions: {},
}));

import { getServerSession } from 'next-auth';
const mockedGetSession = vi.mocked(getServerSession);

// Import after mocks are set up
import { POST as registerHandler } from '../app/api/vendor/register/route';
import { POST as interestHandler } from '../app/api/vendor/interest/route';

describe('Vendor API routes', () => {
  beforeAll(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'easelos-apitest-'));
    const dbPath = path.join(tmpDir, 'vendor.db');
    testDb = new Database(dbPath);
    testDb.pragma('journal_mode = WAL');
    createVendorSchema(testDb);
  });

  afterAll(() => {
    testDb.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('POST /api/vendor/register with valid body returns 201', async () => {
    mockedGetSession.mockResolvedValue({ user: { email: 'api@test.com' } });

    const body = {
      company_name: 'API Test Co',
      contact_name: 'API Tester',
      email: 'api@test.com',
      phone: '555-1234',
      website: 'https://apitest.com',
      city: 'Portland',
      state: 'OR',
      country: 'US',
      capacity: 'low',
      lead_time: '3-7 days',
      machines: [{ machine_type: 'CNC Mill', make_model: 'Test', max_part_size_mm: '200x200' }],
      materials: ['aluminum'],
      certifications: ['ISO 9001'],
    };

    const req = new Request('http://localhost:3000/api/vendor/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const res = await registerHandler(req);
    expect(res.status).toBe(201);
    const data = await res.json();
    expect(data.vendor_id).toBeDefined();
  });

  it('POST /api/vendor/register without auth returns 401', async () => {
    mockedGetSession.mockResolvedValue(null);

    const req = new Request('http://localhost:3000/api/vendor/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: 'Test' }),
    });

    const res = await registerHandler(req);
    expect(res.status).toBe(401);
  });

  it('POST /api/vendor/register with invalid body returns 400', async () => {
    mockedGetSession.mockResolvedValue({ user: { email: 'bad@test.com' } });

    const req = new Request('http://localhost:3000/api/vendor/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_name: '',
        contact_name: '',
        email: 'bad@test.com',
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
      }),
    });

    const res = await registerHandler(req);
    expect(res.status).toBe(400);
  });

  it('POST /api/vendor/interest with valid session creates interest', async () => {
    mockedGetSession.mockResolvedValue({ user: { email: 'api@test.com' } });

    const req = new Request('http://localhost:3000/api/vendor/interest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ part_id: 'bracket-flat-30x20-2xM3-1.5mm-aluminum', category: 'mounting_bracket' }),
    });

    const res = await interestHandler(req);
    expect(res.status).toBe(200);
  });

  it('POST /api/vendor/interest without auth returns 401', async () => {
    mockedGetSession.mockResolvedValue(null);

    const req = new Request('http://localhost:3000/api/vendor/interest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ part_id: 'bracket-1' }),
    });

    const res = await interestHandler(req);
    expect(res.status).toBe(401);
  });

  it('POST /api/vendor/interest with unregistered vendor returns 404', async () => {
    mockedGetSession.mockResolvedValue({ user: { email: 'nobody@test.com' } });

    const req = new Request('http://localhost:3000/api/vendor/interest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ part_id: 'bracket-1' }),
    });

    const res = await interestHandler(req);
    expect(res.status).toBe(404);
  });
});
