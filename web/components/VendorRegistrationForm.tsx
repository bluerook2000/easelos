'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const MACHINE_TYPES = [
  'CNC Mill', 'CNC Lathe', 'Laser CO2', 'Laser Fiber', 'Waterjet',
  '3D Printer FDM', '3D Printer SLS', '3D Printer MJF',
  'Sheet Metal Brake/Bend', 'Other',
] as const;

const MATERIALS = [
  'aluminum', 'steel', 'stainless', 'titanium', 'copper', 'brass',
  'acrylic', 'delrin', 'nylon', 'HDPE', 'polycarbonate', 'wood',
  'carbon fiber', 'custom',
] as const;

const CERTIFICATIONS = [
  'ISO 9001', 'ISO 13485', 'AS9100D', 'ITAR', 'IATF 16949',
  'NADCAP', 'UL', 'CE', 'RoHS', 'Other',
] as const;

const CAPACITIES = [
  { value: 'prototype', label: 'Prototype Only' },
  { value: 'low', label: 'Low Volume (<100/mo)' },
  { value: 'medium', label: 'Medium Volume (100-1000/mo)' },
  { value: 'high', label: 'High Volume (1000+/mo)' },
] as const;

const LEAD_TIMES = [
  '1-3 days', '3-7 days', '1-2 weeks', '2-4 weeks',
] as const;

interface MachineEntry {
  machine_type: string;
  make_model: string;
  max_part_size_mm: string;
}

export default function VendorRegistrationForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const partId = searchParams.get('part_id');
  const category = searchParams.get('category') || '';

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [companyName, setCompanyName] = useState('');
  const [contactName, setContactName] = useState('');
  const [phone, setPhone] = useState('');
  const [website, setWebsite] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('');
  const [capacity, setCapacity] = useState('low');
  const [leadTime, setLeadTime] = useState('1-2 weeks');
  const [machines, setMachines] = useState<MachineEntry[]>([
    { machine_type: '', make_model: '', max_part_size_mm: '' },
  ]);
  const [selectedMaterials, setSelectedMaterials] = useState<string[]>([]);
  const [selectedCerts, setSelectedCerts] = useState<string[]>([]);

  const addMachine = () => {
    setMachines([...machines, { machine_type: '', make_model: '', max_part_size_mm: '' }]);
  };

  const removeMachine = (index: number) => {
    setMachines(machines.filter((_, i) => i !== index));
  };

  const updateMachine = (index: number, field: keyof MachineEntry, value: string) => {
    const updated = [...machines];
    updated[index] = { ...updated[index], [field]: value };
    setMachines(updated);
  };

  const toggleMaterial = (mat: string) => {
    setSelectedMaterials((prev) =>
      prev.includes(mat) ? prev.filter((m) => m !== mat) : [...prev, mat]
    );
  };

  const toggleCert = (cert: string) => {
    setSelectedCerts((prev) =>
      prev.includes(cert) ? prev.filter((c) => c !== cert) : [...prev, cert]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const body = {
      company_name: companyName,
      contact_name: contactName,
      email: '', // overridden by server from session
      phone,
      website,
      city,
      state,
      country,
      capacity,
      lead_time: leadTime,
      machines: machines.filter((m) => m.machine_type !== ''),
      materials: selectedMaterials,
      certifications: selectedCerts,
    };

    try {
      const res = await fetch('/api/vendor/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Registration failed');
      }

      // If there was a part_id, express interest
      if (partId) {
        await fetch('/api/vendor/interest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ part_id: partId, category }),
        });
      }

      router.push('/vendor/dashboard');
    } catch (err: any) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Company Info */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Company Information</legend>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="companyName" className="block text-sm font-medium text-gray-700">
              Company Name *
            </label>
            <input
              id="companyName"
              type="text"
              required
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label htmlFor="contactName" className="block text-sm font-medium text-gray-700">
              Contact Name *
            </label>
            <input
              id="contactName"
              type="text"
              required
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
            <input
              id="phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label htmlFor="website" className="block text-sm font-medium text-gray-700">Website</label>
            <input
              id="website"
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              placeholder="https://"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>
      </fieldset>

      {/* Location */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Location</legend>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="city" className="block text-sm font-medium text-gray-700">City</label>
            <input
              id="city"
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700">State/Province</label>
            <input
              id="state"
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label htmlFor="country" className="block text-sm font-medium text-gray-700">Country</label>
            <input
              id="country"
              type="text"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>
      </fieldset>

      {/* Machines */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Machines</legend>
        <div className="mt-4 space-y-4">
          {machines.map((machine, i) => (
            <div key={i} className="grid gap-4 sm:grid-cols-4 items-end">
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <select
                  value={machine.machine_type}
                  onChange={(e) => updateMachine(i, 'machine_type', e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  <option value="">Select...</option>
                  {MACHINE_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Make/Model</label>
                <input
                  type="text"
                  value={machine.make_model}
                  onChange={(e) => updateMachine(i, 'make_model', e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Max Part Size (mm)</label>
                <input
                  type="text"
                  value={machine.max_part_size_mm}
                  onChange={(e) => updateMachine(i, 'max_part_size_mm', e.target.value)}
                  placeholder="300x200x150"
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>
              <div>
                {machines.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeMachine(i)}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={addMachine}
            className="text-sm text-brand-600 hover:text-brand-700"
          >
            + Add another machine
          </button>
        </div>
      </fieldset>

      {/* Materials */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Materials</legend>
        <p className="mt-1 text-sm text-gray-500">Select all materials you work with.</p>
        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {MATERIALS.map((mat) => (
            <label key={mat} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selectedMaterials.includes(mat)}
                onChange={() => toggleMaterial(mat)}
                className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
              />
              {mat}
            </label>
          ))}
        </div>
      </fieldset>

      {/* Certifications */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Certifications</legend>
        <p className="mt-1 text-sm text-gray-500">Select any certifications your shop holds.</p>
        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
          {CERTIFICATIONS.map((cert) => (
            <label key={cert} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selectedCerts.includes(cert)}
                onChange={() => toggleCert(cert)}
                className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
              />
              {cert}
            </label>
          ))}
        </div>
      </fieldset>

      {/* Capacity & Lead Time */}
      <fieldset>
        <legend className="text-lg font-semibold text-gray-900">Capacity & Lead Time</legend>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="capacity" className="block text-sm font-medium text-gray-700">
              Production Capacity
            </label>
            <select
              id="capacity"
              value={capacity}
              onChange={(e) => setCapacity(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {CAPACITIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="leadTime" className="block text-sm font-medium text-gray-700">
              Typical Lead Time
            </label>
            <select
              id="leadTime"
              value={leadTime}
              onChange={(e) => setLeadTime(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {LEAD_TIMES.map((lt) => (
                <option key={lt} value={lt}>{lt}</option>
              ))}
            </select>
          </div>
        </div>
      </fieldset>

      {/* Submit */}
      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-brand-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Registering...' : 'Register as Vendor'}
        </button>
      </div>
    </form>
  );
}
