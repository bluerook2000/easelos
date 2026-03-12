'use client';

import { useState } from 'react';
import type { PartPricing } from '@/lib/types';
import { MATERIAL_LABELS, QUANTITIES } from '@/lib/constants';

interface PricingTableProps {
  pricing: PartPricing;
  defaultMaterial: string;
}

export default function PricingTable({ pricing, defaultMaterial }: PricingTableProps) {
  const [material, setMaterial] = useState(defaultMaterial);

  const materials = Object.keys(pricing);

  return (
    <div>
      {/* Material switcher */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Material</label>
        <div className="flex flex-wrap gap-2">
          {materials.map((mat) => (
            <button
              key={mat}
              onClick={() => setMaterial(mat)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                material === mat
                  ? 'bg-brand-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {MATERIAL_LABELS[mat] || mat}
            </button>
          ))}
        </div>
      </div>

      {/* Pricing table */}
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="py-2 text-left font-medium text-gray-500">Quantity</th>
            <th className="py-2 text-right font-medium text-gray-500">Price / Part</th>
            <th className="py-2 text-right font-medium text-gray-500">Total</th>
          </tr>
        </thead>
        <tbody>
          {QUANTITIES.map((qty) => {
            const pricePerPart = pricing[material]?.[qty];
            if (pricePerPart == null) return null;
            const total = pricePerPart * Number(qty);
            return (
              <tr key={qty} className="border-b border-gray-100">
                <td className="py-2 text-gray-900">{Number(qty).toLocaleString()}</td>
                <td className="py-2 text-right font-medium text-gray-900">
                  ${pricePerPart.toFixed(2)}
                </td>
                <td className="py-2 text-right text-gray-500">
                  ${total.toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
