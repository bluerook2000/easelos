export const CATEGORY_NAMES: Record<string, string> = {
  mounting_bracket: 'Mounting Brackets',
  motor_mount: 'Motor Mounts',
  gusset_plate: 'Gusset Plates',
  base_plate: 'Base Plates',
  standoff: 'Standoffs',
  sensor_mount: 'Sensor Mounts',
  electronics_panel: 'Electronics Panels',
  bearing_plate: 'Bearing Plates',
  cable_bracket: 'Cable Brackets',
};

export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  mounting_bracket: 'L-brackets, U-brackets, and flat mounting plates with metric hole patterns for equipment and component mounting.',
  motor_mount: 'NEMA 17, 23, and 34 motor mount plates with pilot holes and bolt circle patterns.',
  gusset_plate: 'Corner and T-junction reinforcement plates for structural connections.',
  base_plate: 'Chassis and base plates with grid-pattern mounting holes.',
  standoff: 'Round standoff plates with center and perimeter mounting holes.',
  sensor_mount: 'Proximity sensor and limit switch mounting brackets.',
  electronics_panel: 'Enclosure panels and DIN rail mount plates for electronics.',
  bearing_plate: '608 and 6201 bearing mount plates with bore and bolt circle holes.',
  cable_bracket: 'Cable clip and guide brackets for wire management.',
};

export const CATEGORY_LABELS: Record<string, string> = {
  mounting_bracket: 'Mounting Bracket',
  motor_mount: 'Motor Mount',
  gusset_plate: 'Gusset Plate',
  base_plate: 'Base Plate',
  standoff: 'Standoff',
  sensor_mount: 'Sensor Mount',
  electronics_panel: 'Electronics Panel',
  bearing_plate: 'Bearing Plate',
  cable_bracket: 'Cable Bracket',
};

export const MATERIAL_LABELS: Record<string, string> = {
  aluminum: '5052-H32 Aluminum',
  steel: 'A1011 Carbon Steel',
  stainless: '304 Stainless Steel',
};

export const QUANTITIES = ['1', '10', '100', '500', '1000', '10000'] as const;
