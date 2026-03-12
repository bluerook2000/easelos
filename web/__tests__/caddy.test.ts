import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const WEB_DIR = path.resolve(__dirname, '..');
const CADDYFILE = path.join(WEB_DIR, 'Caddyfile');

describe('Caddyfile configuration', () => {
  const content = fs.readFileSync(CADDYFILE, 'utf-8');

  it('listens on port 8099', () => {
    expect(content).toContain(':8099');
  });

  it('uses reverse_proxy to Next.js', () => {
    expect(content).toMatch(/reverse_proxy\s+localhost:3000/);
  });

  it('does not use file_server (SSR mode)', () => {
    expect(content).not.toContain('file_server');
  });

  it('includes security headers', () => {
    expect(content).toContain('X-Content-Type-Options');
    expect(content).toContain('X-Frame-Options');
  });

  it('enables gzip compression', () => {
    expect(content).toContain('encode gzip');
  });
});
