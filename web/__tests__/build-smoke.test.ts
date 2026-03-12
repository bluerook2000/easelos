import { describe, it, expect, beforeAll } from 'vitest';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const WEB_DIR = path.resolve(__dirname, '..');
const OUT_DIR = path.join(WEB_DIR, 'out');

describe('Build smoke test', () => {
  beforeAll(() => {
    try {
      execSync('npx tsx scripts/ingest.ts', { cwd: WEB_DIR, stdio: 'pipe', timeout: 60000 });
    } catch {
      // Ingestion may fail if no pipeline output
    }
    execSync('npx next build', { cwd: WEB_DIR, stdio: 'pipe', timeout: 120000 });
  }, 180000);

  it('generates out/ directory', () => {
    expect(fs.existsSync(OUT_DIR)).toBe(true);
  });

  it('generates index.html', () => {
    expect(fs.existsSync(path.join(OUT_DIR, 'index.html'))).toBe(true);
  });

  it('generates search page', () => {
    expect(fs.existsSync(path.join(OUT_DIR, 'search', 'index.html'))).toBe(true);
  });

  it('generates sitemap.xml', () => {
    expect(fs.existsSync(path.join(OUT_DIR, 'sitemap.xml'))).toBe(true);
  });

  it('generates robots.txt', () => {
    expect(fs.existsSync(path.join(OUT_DIR, 'robots.txt'))).toBe(true);
  });

  it('generates vendor placeholder page', () => {
    expect(fs.existsSync(path.join(OUT_DIR, 'vendor', 'register', 'index.html'))).toBe(true);
  });

  it('index.html contains "Easelos"', () => {
    const html = fs.readFileSync(path.join(OUT_DIR, 'index.html'), 'utf-8');
    expect(html).toContain('Easelos');
  });
});
