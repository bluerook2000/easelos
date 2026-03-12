import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { getVendorDb, getAllVendors } from '@/lib/vendor-db';

export async function GET(request: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Check admin access
  const adminEmails = (process.env.ADMIN_EMAILS || '')
    .split(',')
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);

  if (!adminEmails.includes(session.user.email.toLowerCase())) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const { searchParams } = new URL(request.url);
  const filter = {
    material: searchParams.get('material') || undefined,
    machine_type: searchParams.get('machine_type') || undefined,
    certification: searchParams.get('certification') || undefined,
    capacity: searchParams.get('capacity') || undefined,
  };

  const db = getVendorDb();
  const vendors = getAllVendors(db, filter);

  return NextResponse.json({ vendors, total: vendors.length });
}
