interface DownloadButtonsProps {
  category: string;
  partId: string;
}

export default function DownloadButtons({ category, partId }: DownloadButtonsProps) {
  const basePath = `/parts/${category}/${partId}`;
  const files = [
    { label: 'STEP', path: `${basePath}/part.step`, desc: '3D CAD file' },
    { label: 'SVG', path: `${basePath}/profile.svg`, desc: '2D profile' },
    { label: 'DXF', path: `${basePath}/profile.dxf`, desc: 'Laser cutting' },
  ];

  return (
    <div className="flex flex-wrap gap-3">
      {files.map((file) => (
        <a
          key={file.label}
          href={file.path}
          download
          className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <span className="mr-2 text-xs font-bold text-brand-600">{file.label}</span>
          {file.desc}
        </a>
      ))}
    </div>
  );
}
