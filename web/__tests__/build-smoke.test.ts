import { describe, it, expect, beforeAll } from 'vitest';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const WEB_DIR = path.resolve(__dirname, '..');
const NEXT_DIR = path.join(WEB_DIR, '.next');

describe('Build smoke test', () => {
  beforeAll(() => {
    try {
      execSync('npx tsx scripts/ingest.ts', { cwd: WEB_DIR, stdio: 'pipe', timeout: 60000 });
    } catch {
      // Ingestion may fail if no pipeline output
    }
    execSync('npx next build', {
      cwd: WEB_DIR,
      stdio: 'pipe',
      timeout: 120000,
      env: { ...process.env, NEXTAUTH_SECRET: 'build-test-secret' },
    });
  }, 180000);

  it('generates .next/ build directory', () => {
    expect(fs.existsSync(NEXT_DIR)).toBe(true);
  });

  it('generates server output', () => {
    expect(fs.existsSync(path.join(NEXT_DIR, 'server'))).toBe(true);
  });

  it('generates server app directory for static pages', () => {
    // In hybrid SSR/SSG mode, statically generated pages are in .next/server/app/
    const serverAppDir = path.join(NEXT_DIR, 'server', 'app');
    expect(fs.existsSync(serverAppDir)).toBe(true);
  });

  it('build output includes routes-manifest', () => {
    expect(fs.existsSync(path.join(NEXT_DIR, 'routes-manifest.json'))).toBe(true);
  });

  it('does not produce out/ directory (no longer static export)', () => {
    // Verify we are NOT in static export mode anymore
    expect(fs.existsSync(path.join(WEB_DIR, 'out', 'index.html'))).toBe(false);
  });

  it('includes API routes in build output', () => {
    // Verify that API routes (auth, vendor, admin) are compiled into the server build
    const routesManifest = JSON.parse(fs.readFileSync(path.join(NEXT_DIR, 'routes-manifest.json'), 'utf-8'));
    const allRoutes = [
      ...(routesManifest.staticRoutes || []).map((r: any) => r.page),
      ...(routesManifest.dynamicRoutes || []).map((r: any) => r.page),
    ];
    // At least the auth catch-all route must exist
    expect(allRoutes.some((r: string) => r.includes('auth'))).toBe(true);
  });
});
