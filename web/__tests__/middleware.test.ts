import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock next-auth/jwt before importing middleware
vi.mock('next-auth/jwt', () => ({
  getToken: vi.fn(),
}));

import { getToken } from 'next-auth/jwt';
import { middleware, config } from '../middleware';
import { NextRequest } from 'next/server';

const mockedGetToken = vi.mocked(getToken);

function makeRequest(path: string): NextRequest {
  return new NextRequest(new URL(path, 'http://localhost:3000'));
}

describe('Middleware', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('exports matcher config for vendor and admin routes', () => {
    expect(config.matcher).toBeDefined();
    expect(config.matcher).toContain('/vendor/:path*');
    expect(config.matcher).toContain('/admin/:path*');
  });

  it('redirects unauthenticated user from /vendor/dashboard to signin', async () => {
    mockedGetToken.mockResolvedValue(null);
    const req = makeRequest('/vendor/dashboard');
    const res = await middleware(req);
    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toContain('/auth/signin');
  });

  it('allows authenticated user to access /vendor/dashboard', async () => {
    mockedGetToken.mockResolvedValue({ email: 'test@test.com' } as any);
    const req = makeRequest('/vendor/dashboard');
    const res = await middleware(req);
    // NextResponse.next() returns 200
    expect(res.status).toBe(200);
  });

  it('redirects unauthenticated user from /admin to signin', async () => {
    mockedGetToken.mockResolvedValue(null);
    const req = makeRequest('/admin');
    const res = await middleware(req);
    expect(res.status).toBe(307);
  });

  it('redirects non-admin user from /admin to forbidden page', async () => {
    process.env.ADMIN_EMAILS = 'admin@easelos.com';
    mockedGetToken.mockResolvedValue({ email: 'vendor@test.com' } as any);
    const req = makeRequest('/admin');
    const res = await middleware(req);
    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toContain('/admin/forbidden');
    delete process.env.ADMIN_EMAILS;
  });

  it('allows admin user to access /admin', async () => {
    process.env.ADMIN_EMAILS = 'admin@easelos.com,other@easelos.com';
    mockedGetToken.mockResolvedValue({ email: 'admin@easelos.com' } as any);
    const req = makeRequest('/admin');
    const res = await middleware(req);
    expect(res.status).toBe(200);
    delete process.env.ADMIN_EMAILS;
  });
});
