export interface SearchEntry {
  id: string;   // part_id
  c: string;    // category
  n: string;    // name
  m: string;    // material
  k: string;    // keywords (description + hole sizes, lowercase)
}

export function searchParts(
  index: SearchEntry[],
  query: string,
  limit = 50,
): SearchEntry[] {
  if (!query.trim()) {
    return index.slice(0, limit);
  }

  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);

  const results = index.filter((entry) => {
    const searchable = `${entry.n} ${entry.c} ${entry.m} ${entry.k}`.toLowerCase();
    return terms.every((term) => searchable.includes(term));
  });

  return results.slice(0, limit);
}
