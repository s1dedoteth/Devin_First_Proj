export interface FlashIdInfoRaw {
  s: number;  // Die
  p: number;  // Plane
  b: number;  // Block
  t: string[];  // Controllers
  n: string[];  // Part Numbers
}

export interface FlashIdInfo {
  s: number;  // Die
  p: number;  // Plane
  b: number;  // Block
  t: string[];  // Controllers
  n: string[];  // Part Numbers
  vendor: string;
  cellLevel: string;
  density: string;
  processNode: string;
  voltage: string;
  ext: Record<string, string>;
}
