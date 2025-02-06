import type { Classification } from './Classification.js';
import type { FlashInterface } from './FlashInterface.js';

export interface FlashInfo {
  partNumber: string;
  vendor: string;
  type: string;
  density: string;
  deviceWidth: number;
  cellLevel: string;
  processNode: string;
  generation: string;
  interface: FlashInterface;
  classification: Classification;
  voltage: string;
  package: string;
  controller: string[];
  remark: string;
  extraInfo: Record<string, string>;
  flashId: string[];
  productionDate?: string;
}
