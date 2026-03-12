'use client';

import { useRef, useEffect, useState } from 'react';

interface ModelViewerProps {
  glbUrl: string;
  fallbackSvgUrl: string;
  alt: string;
}

/**
 * Lightweight 3D model viewer using Google's model-viewer web component.
 * Falls back to SVG if model-viewer is unavailable or the glb fails to load.
 */
export default function ModelViewer({ glbUrl, fallbackSvgUrl, alt }: ModelViewerProps) {
  const [hasError, setHasError] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const loadViewer = async () => {
      try {
        // Dynamically load the model-viewer polyfill
        if (!customElements.get('model-viewer')) {
          const script = document.createElement('script');
          script.type = 'module';
          script.src = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@3/dist/model-viewer.min.js';
          await new Promise<void>((resolve, reject) => {
            script.onload = () => resolve();
            script.onerror = () => reject();
            document.head.appendChild(script);
          });
        }
        // Create model-viewer element imperatively to avoid JSX type issues
        if (containerRef.current) {
          const mv = document.createElement('model-viewer');
          mv.setAttribute('src', glbUrl);
          mv.setAttribute('alt', alt);
          mv.setAttribute('auto-rotate', '');
          mv.setAttribute('camera-controls', '');
          mv.setAttribute('shadow-intensity', '1');
          mv.style.width = '100%';
          mv.style.height = '320px';
          mv.addEventListener('error', () => setHasError(true));
          containerRef.current.innerHTML = '';
          containerRef.current.appendChild(mv);
          setLoaded(true);
        }
      } catch {
        setHasError(true);
      }
    };

    loadViewer();
  }, [glbUrl, alt]);

  if (hasError) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-gray-50 p-8">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={fallbackSvgUrl} alt={alt} className="max-h-80 w-full object-contain" />
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-2" data-testid="model-viewer-container">
      <div ref={containerRef}>
        {!loaded && (
          <div className="flex items-center justify-center" style={{ height: '320px' }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={fallbackSvgUrl} alt={alt} className="max-h-60 object-contain" />
          </div>
        )}
      </div>
    </div>
  );
}
