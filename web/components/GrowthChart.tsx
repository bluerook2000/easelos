import type { GrowthEntry } from '@/lib/types';

interface GrowthChartProps {
  data: GrowthEntry[];
  width?: number;
  height?: number;
}

export default function GrowthChart({ data, width = 600, height = 200 }: GrowthChartProps) {
  if (data.length === 0) {
    return <p className="text-sm text-gray-500">No growth data yet.</p>;
  }

  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const maxParts = Math.max(...data.map((d) => d.total_parts));
  const yScale = chartH / (maxParts * 1.1);
  const xStep = data.length > 1 ? chartW / (data.length - 1) : chartW;

  const points = data.map((d, i) => ({
    x: padding.left + i * xStep,
    y: padding.top + chartH - d.total_parts * yScale,
    label: d.date,
    value: d.total_parts,
  }));

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${pathD} L ${points[points.length - 1].x} ${padding.top + chartH} L ${points[0].x} ${padding.top + chartH} Z`;

  return (
    <div className="w-full overflow-x-auto">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full max-w-[600px]"
        role="img"
        aria-label="Catalog growth chart"
      >
        <text x={padding.left - 8} y={padding.top + 4} textAnchor="end" className="fill-gray-400 text-[10px]">
          {maxParts.toLocaleString()}
        </text>
        <text x={padding.left - 8} y={padding.top + chartH + 4} textAnchor="end" className="fill-gray-400 text-[10px]">
          0
        </text>
        <path d={areaD} className="fill-brand-100 opacity-50" />
        <path d={pathD} className="stroke-brand-500" fill="none" strokeWidth="2" />
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" className="fill-brand-600" />
        ))}
        {data.length > 0 && (
          <>
            <text x={points[0].x} y={height - 5} textAnchor="start" className="fill-gray-400 text-[10px]">
              {data[0].date}
            </text>
            {data.length > 1 && (
              <text x={points[points.length - 1].x} y={height - 5} textAnchor="end" className="fill-gray-400 text-[10px]">
                {data[data.length - 1].date}
              </text>
            )}
          </>
        )}
        {points.length > 0 && (
          <text
            x={points[points.length - 1].x}
            y={points[points.length - 1].y - 8}
            textAnchor="middle"
            className="fill-brand-700 text-xs font-semibold"
          >
            {points[points.length - 1].value.toLocaleString()} parts
          </text>
        )}
      </svg>
    </div>
  );
}
