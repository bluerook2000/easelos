import type { NextAuthOptions } from 'next-auth';
import EmailProvider from 'next-auth/providers/email';
import { VendorDbAdapter } from './auth-adapter';

function getSecret(): string {
  if (process.env.NEXTAUTH_SECRET) {
    return process.env.NEXTAUTH_SECRET;
  }
  if (process.env.NODE_ENV === 'production') {
    throw new Error('NEXTAUTH_SECRET environment variable is required in production');
  }
  return 'dev-secret-do-not-use-in-production';
}

export const authOptions: NextAuthOptions = {
  adapter: VendorDbAdapter(),
  providers: [
    EmailProvider({
      server: process.env.EMAIL_SERVER || { jsonTransport: true },
      from: process.env.EMAIL_FROM || 'noreply@easelos.com',
      ...(process.env.EMAIL_SERVER ? {} : {
        sendVerificationRequest: async ({ identifier: email, url }) => {
          console.log(`\n[EASELOS AUTH] Magic link for ${email}:\n${url}\n`);
        },
      }),
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/auth/signin',
    verifyRequest: '/auth/verify-request',
  },
  secret: getSecret(),
  callbacks: {
    async jwt({ token, user }) {
      if (user?.email) {
        token.email = user.email;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user && token.email) {
        session.user.email = token.email as string;
      }
      return session;
    },
  },
};
