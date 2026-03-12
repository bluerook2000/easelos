import { describe, it, expect } from 'vitest';
import { authOptions } from '../lib/auth';

describe('NextAuth configuration', () => {
  it('exports valid authOptions', () => {
    expect(authOptions).toBeDefined();
    expect(authOptions.providers).toBeDefined();
    expect(authOptions.providers.length).toBeGreaterThan(0);
  });

  it('uses email provider', () => {
    const emailProvider = authOptions.providers.find(
      (p: any) => p.id === 'email' || p.type === 'email'
    );
    expect(emailProvider).toBeDefined();
  });

  it('uses jwt session strategy', () => {
    expect(authOptions.session?.strategy).toBe('jwt');
  });

  it('has custom sign-in page configured', () => {
    expect(authOptions.pages?.signIn).toBe('/auth/signin');
  });

  it('has callbacks defined', () => {
    expect(authOptions.callbacks).toBeDefined();
    expect(authOptions.callbacks?.jwt).toBeDefined();
    expect(authOptions.callbacks?.session).toBeDefined();
  });

  it('has an adapter configured with verification token methods', () => {
    expect(authOptions.adapter).toBeDefined();
    expect(authOptions.adapter?.createVerificationToken).toBeDefined();
    expect(authOptions.adapter?.useVerificationToken).toBeDefined();
  });

  it('has an adapter with working user methods for email provider flow', () => {
    expect(authOptions.adapter?.createUser).toBeDefined();
    expect(authOptions.adapter?.getUser).toBeDefined();
    expect(authOptions.adapter?.getUserByEmail).toBeDefined();
    expect(typeof authOptions.adapter?.createUser).toBe('function');
    expect(typeof authOptions.adapter?.getUserByEmail).toBe('function');
  });
});
