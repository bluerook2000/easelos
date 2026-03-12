import type { MetadataRoute } from 'next';
import { getDb, getAllCategories, getPartsByCategory } from '@/lib/db';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://easelos.com';
  const entries: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/search`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.5,
    },
  ];

  try {
    const db = getDb();
    const categories = getAllCategories(db);

    for (const cat of categories) {
      entries.push({
        url: `${baseUrl}/parts/${cat.slug}`,
        lastModified: new Date(),
        changeFrequency: 'daily',
        priority: 0.8,
      });

      const parts = getPartsByCategory(db, cat.slug);
      for (const part of parts) {
        entries.push({
          url: `${baseUrl}/parts/${part.category}/${part.part_id}`,
          lastModified: new Date(),
          changeFrequency: 'weekly',
          priority: 0.6,
        });
      }
    }
  } catch {
    // Database not available during initial build
  }

  return entries;
}
