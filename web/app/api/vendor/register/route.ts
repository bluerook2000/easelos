import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { getVendorDb, createVendor } from '@/lib/vendor-db';

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();

    // Override email with session email to prevent spoofing
    body.email = session.user.email;

    const db = getVendorDb();
    const vendorId = createVendor(db, body);

    return NextResponse.json({ vendor_id: vendorId }, { status: 201 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Registration failed' },
      { status: 400 }
    );
  }
}
