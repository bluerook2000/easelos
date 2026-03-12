import type { Adapter, AdapterUser, VerificationToken } from 'next-auth/adapters';
import { randomUUID } from 'crypto';
import { getVendorDb } from './vendor-db';

/**
 * Custom NextAuth adapter for vendor.db.
 * Handles verification tokens and lightweight user records.
 * User records (nextauth_users table) exist solely to satisfy NextAuth's
 * internal email provider flow. The vendor's real profile lives in the
 * vendors table. Sessions use JWT — no session/account tables needed.
 */
export function VendorDbAdapter(): Adapter {
  return {
    createUser(user: Omit<AdapterUser, 'id'>): Promise<AdapterUser> {
      const db = getVendorDb();
      const id = randomUUID();
      db.prepare(
        'INSERT INTO nextauth_users (id, email, email_verified) VALUES (?, ?, ?)'
      ).run(id, user.email, user.emailVerified?.toISOString() || null);
      return Promise.resolve({ id, email: user.email, emailVerified: user.emailVerified ?? null });
    },
    getUser(id: string): Promise<AdapterUser | null> {
      const db = getVendorDb();
      const row = db.prepare('SELECT id, email, email_verified FROM nextauth_users WHERE id = ?').get(id) as any;
      if (!row) return Promise.resolve(null);
      return Promise.resolve({ id: row.id, email: row.email, emailVerified: row.email_verified ? new Date(row.email_verified) : null });
    },
    getUserByEmail(email: string): Promise<AdapterUser | null> {
      const db = getVendorDb();
      const row = db.prepare('SELECT id, email, email_verified FROM nextauth_users WHERE email = ?').get(email) as any;
      if (!row) return Promise.resolve(null);
      return Promise.resolve({ id: row.id, email: row.email, emailVerified: row.email_verified ? new Date(row.email_verified) : null });
    },
    getUserByAccount(): Promise<AdapterUser | null> {
      return Promise.resolve(null);
    },
    updateUser(user: Partial<AdapterUser> & Pick<AdapterUser, 'id'>): Promise<AdapterUser> {
      const db = getVendorDb();
      const existing = db.prepare('SELECT id, email, email_verified FROM nextauth_users WHERE id = ?').get(user.id) as any;
      if (!existing) throw new Error('User not found');
      if (user.email !== undefined) {
        db.prepare('UPDATE nextauth_users SET email = ? WHERE id = ?').run(user.email, user.id);
      }
      if (user.emailVerified !== undefined) {
        db.prepare('UPDATE nextauth_users SET email_verified = ? WHERE id = ?').run(user.emailVerified?.toISOString() || null, user.id);
      }
      const updated = db.prepare('SELECT id, email, email_verified FROM nextauth_users WHERE id = ?').get(user.id) as any;
      return Promise.resolve({ id: updated.id, email: updated.email, emailVerified: updated.email_verified ? new Date(updated.email_verified) : null });
    },
    createVerificationToken(verificationToken: VerificationToken): Promise<VerificationToken> {
      const db = getVendorDb();
      db.prepare(
        'INSERT INTO verification_tokens (identifier, token, expires) VALUES (?, ?, ?)'
      ).run(verificationToken.identifier, verificationToken.token, verificationToken.expires.toISOString());
      return Promise.resolve(verificationToken);
    },
    useVerificationToken({ identifier, token }: { identifier: string; token: string }): Promise<VerificationToken | null> {
      const db = getVendorDb();
      const row = db.prepare(
        'SELECT identifier, token, expires FROM verification_tokens WHERE identifier = ? AND token = ?'
      ).get(identifier, token) as { identifier: string; token: string; expires: string } | undefined;
      if (!row) return Promise.resolve(null);
      db.prepare(
        'DELETE FROM verification_tokens WHERE identifier = ? AND token = ?'
      ).run(identifier, token);
      return Promise.resolve({
        identifier: row.identifier,
        token: row.token,
        expires: new Date(row.expires),
      });
    },
    // Stubs for interface methods not needed with JWT sessions
    linkAccount: () => Promise.resolve(undefined as any),
    createSession: () => Promise.reject(new Error('Not implemented — using JWT sessions')),
    getSessionAndUser: () => Promise.resolve(null),
    updateSession: () => Promise.resolve(null),
    deleteSession: () => Promise.resolve(undefined),
    unlinkAccount: () => Promise.resolve(undefined),
    deleteUser: () => Promise.resolve(undefined),
  };
}
