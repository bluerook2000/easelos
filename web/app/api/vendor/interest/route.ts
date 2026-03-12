import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { getVendorDb, getVendorByEmail, createVendorInterest } from '@/lib/vendor-db';

// GET: "I Can Make This" button redirect flow
export async function GET(request: NextRequest) {
  const partId = request.nextUrl.searchParams.get('part_id');
  const category = request.nextUrl.searchParams.get('category') || '';

  if (!partId) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  const session = await getServerSession(authOptions);

  // 1. Not authenticated — redirect to sign-in, then back here
  if (!session?.user?.email) {
    const signInUrl = new URL('/auth/signin', request.url);
    signInUrl.searchParams.set('callbackUrl', request.url);
    return NextResponse.redirect(signInUrl);
  }

  // 2. Authenticated but not registered — redirect to registration with part_id
  const db = getVendorDb();
  const vendor = getVendorByEmail(db, session.user.email);
  if (!vendor) {
    const registerUrl = new URL('/vendor/register', request.url);
    registerUrl.searchParams.set('part_id', partId);
    if (category) registerUrl.searchParams.set('category', category);
    return NextResponse.redirect(registerUrl);
  }

  // 3. Authenticated and registered — create interest and go to dashboard
  createVendorInterest(db, vendor.id, partId, category);
  return NextResponse.redirect(new URL('/vendor/dashboard', request.url));
}

// POST: Direct API call (e.g., from registration form)
export async function POST(request: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const partId = body.part_id;
  const category = body.category || '';
  if (!partId || typeof partId !== 'string') {
    return NextResponse.json({ error: 'part_id is required' }, { status: 400 });
  }

  const db = getVendorDb();
  const vendor = getVendorByEmail(db, session.user.email);
  if (!vendor) {
    return NextResponse.json(
      { error: 'Vendor profile not found. Please register first.' },
      { status: 404 }
    );
  }

  createVendorInterest(db, vendor.id, partId, category);
  return NextResponse.json({ success: true });
}
