export interface HoleSpec {
  size: string;
  diameter_mm: number;
  x_mm: number;
  y_mm: number;
}

export interface PartPricing {
  [material: string]: {
    [quantity: string]: number;
  };
}

export interface Part {
  part_id: string;
  category: string;
  name: string;
  description: string;
  width_mm: number;
  height_mm: number;
  thickness_mm: number;
  width_in: number;
  height_in: number;
  area_sq_in: number;
  hole_count: number;
  hole_specs: HoleSpec[];
  material: string;
  material_name: string;
  weight_estimate_g: number;
  complexity: string;
  size_category: string;
  pricing: PartPricing;
  files: {
    step: string;
    svg: string;
    dxf: string;
    png: string;
    metadata: string;
  };
}

export interface CategorySummary {
  slug: string;
  name: string;
  part_count: number;
  description: string;
}

export interface GrowthEntry {
  date: string;
  total_parts: number;
  by_category: Record<string, number>;
}
