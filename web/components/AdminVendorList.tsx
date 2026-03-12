'use client';

import { useState, useEffect } from 'react';

interface Vendor {
  id: number;
  company_name: string;
  contact_name: string;
  email: string;
  city: string;
  state: string;
  country: string;
  capacity: string;
  lead_time: string;
  machines: Array<{ machine_type: string; make_model: string }>;
  materials: string[];
  certifications: string[];
}

const MACHINE_TYPES = [
  'CNC Mill', 'CNC Lathe', 'Laser CO2', 'Laser Fiber', 'Waterjet',
  '3D Printer FDM', '3D Printer SLS', '3D Printer MJF',
  'Sheet Metal Brake/Bend', 'Other',
];

const MATERIALS = [
  'aluminum', 'steel', 'stainless', 'titanium', 'copper', 'brass',
  'acrylic', 'delrin', 'nylon', 'HDPE', 'polycarbonate', 'wood',
  'carbon fiber', 'custom',
];

const CERTIFICATIONS = [
  'ISO 9001', 'ISO 13485', 'AS9100D', 'ITAR', 'IATF 16949',
  'NADCAP', 'UL', 'CE', 'RoHS', 'Other',
];

const CAPACITIES = ['prototype', 'low', 'medium', 'high'];

export default function AdminVendorList() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [material, setMaterial] = useState('');
  const [machineType, setMachineType] = useState('');
  const [certification, setCertification] = useState('');
  const [capacity, setCapacity] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);

    const params = new URLSearchParams();
    if (material) params.set('material', material);
    if (machineType) params.set('machine_type', machineType);
    if (certification) params.set('certification', certification);
    if (capacity) params.set('capacity', capacity);

    fetch(`/api/admin/vendors?${params}`, { signal: controller.signal })
      .then((res) => res.ok ? res.json() : Promise.reject())
      .then((data) => {
        setVendors(data.vendors);
        setTotal(data.total);
        setLoading(false);
      })
      .catch((err) => {
        if (err?.name !== 'AbortError') setLoading(false);
      });

    return () => controller.abort();
  }, [material, machineType, certification, capacity]);

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <div>
          <label className="block text-xs font-medium text-gray-500">Machine Type</label>
          <select
            value={machineType}
            onChange={(e) => setMachineType(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
          >
            <option value="">All</option>
            {MACHINE_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Material</label>
          <select
            value={material}
            onChange={(e) => setMaterial(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
          >
            <option value="">All</option>
            {MATERIALS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Certification</label>
          <select
            value={certification}
            onChange={(e) => setCertification(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
          >
            <option value="">All</option>
            {CERTIFICATIONS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Capacity</label>
          <select
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
          >
            <option value="">All</option>
            {CAPACITIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      <p className="mb-4 text-sm text-gray-500">{total} vendor{total !== 1 ? 's' : ''} found</p>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : vendors.length === 0 ? (
        <p className="text-gray-500">No vendors match the selected filters.</p>
      ) : (
        <div className="space-y-4">
          {vendors.map((vendor) => (
            <div key={vendor.id} className="rounded-lg border border-gray-200 bg-white p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{vendor.company_name}</h3>
                  <p className="text-sm text-gray-500">
                    {vendor.contact_name} &middot; {vendor.email}
                  </p>
                  {(vendor.city || vendor.state || vendor.country) && (
                    <p className="text-sm text-gray-500">
                      {[vendor.city, vendor.state, vendor.country].filter(Boolean).join(', ')}
                    </p>
                  )}
                </div>
                <div className="text-right text-sm">
                  <span className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">
                    {vendor.capacity}
                  </span>
                  <p className="mt-1 text-xs text-gray-500">{vendor.lead_time}</p>
                </div>
              </div>

              {vendor.machines.length > 0 && (
                <div className="mt-3">
                  <span className="text-xs font-medium text-gray-500">Machines: </span>
                  <span className="text-xs text-gray-700">
                    {vendor.machines.map((m) => `${m.machine_type}${m.make_model ? ` (${m.make_model})` : ''}`).join(', ')}
                  </span>
                </div>
              )}

              {vendor.materials.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {vendor.materials.map((m) => (
                    <span key={m} className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{m}</span>
                  ))}
                </div>
              )}

              {vendor.certifications.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {vendor.certifications.map((c) => (
                    <span key={c} className="inline-flex rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">{c}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
