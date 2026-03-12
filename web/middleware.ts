import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(request: NextRequest): Promise<NextResponse> {
  const token = await getToken({ req: request });
  const { pathname } = request.nextUrl;

  // Unauthenticated: redirect to sign-in
  if (!token) {
    const signInUrl = new URL('/auth/signin', request.url);
    signInUrl.searchParams.set('callbackUrl', request.url);
    return NextResponse.redirect(signInUrl);
  }

  // Admin route: check email allowlist (skip the forbidden page itself to avoid redirect loops)
  if (pathname.startsWith('/admin') && pathname !== '/admin/forbidden') {
    const adminEmails = (process.env.ADMIN_EMAILS || '')
      .split(',')
      .map((e) => e.trim().toLowerCase())
      .filter(Boolean);

    const userEmail = (token.email as string || '').toLowerCase();
    if (!adminEmails.includes(userEmail)) {
      return NextResponse.redirect(new URL('/admin/forbidden', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/vendor/:path*', '/admin/:path*'],
};
