import type { HoleSpec } from '@/lib/types';

interface PartSpecsProps {
  width_mm: number;
  height_mm: number;
  thickness_mm: number;
  weight_estimate_g: number;
  material_name: string;
  hole_count: number;
  hole_specs: HoleSpec[];
  complexity: string;
  size_category: string;
}

export default function PartSpecs(props: PartSpecsProps) {
  const holeSizes = [...new Set(props.hole_specs.map((h) => h.size))];

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-3">Specifications</h2>
      <table className="w-full text-sm">
        <tbody>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Dimensions</td>
            <td className="py-2 text-right text-gray-900">
              {props.width_mm} x {props.height_mm} x {props.thickness_mm} mm
            </td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Material</td>
            <td className="py-2 text-right text-gray-900">{props.material_name}</td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Weight (est.)</td>
            <td className="py-2 text-right text-gray-900">{props.weight_estimate_g}g</td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Holes</td>
            <td className="py-2 text-right text-gray-900">
              {props.hole_count} ({holeSizes.join(', ') || 'none'})
            </td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Complexity</td>
            <td className="py-2 text-right text-gray-900 capitalize">{props.complexity}</td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-2 text-gray-500">Size Class</td>
            <td className="py-2 text-right text-gray-900 capitalize">{props.size_category}</td>
          </tr>
        </tbody>
      </table>

      {props.hole_specs.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Hole Positions</h3>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="py-1 text-left text-gray-500">Size</th>
                <th className="py-1 text-right text-gray-500">Diameter (mm)</th>
                <th className="py-1 text-right text-gray-500">X (mm)</th>
                <th className="py-1 text-right text-gray-500">Y (mm)</th>
              </tr>
            </thead>
            <tbody>
              {props.hole_specs.map((hole, i) => (
                <tr key={i} className="border-b border-gray-50">
                  <td className="py-1 text-gray-900">{hole.size}</td>
                  <td className="py-1 text-right text-gray-900">{hole.diameter_mm}</td>
                  <td className="py-1 text-right text-gray-900">{hole.x_mm}</td>
                  <td className="py-1 text-right text-gray-900">{hole.y_mm}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
