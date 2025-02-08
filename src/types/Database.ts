import type { FlashIdInfo } from './FlashIdInfo.js';

export interface PartNumberInfo {
  id: string[];  // Flash IDs
  l?: string;    // Process node
  c?: string;    // Cell level
  v?: string;    // Voltage
  i?: {         // Interface
    async: boolean;
    sync: boolean;
    toggle: boolean;
  };
  t?: string[];  // Controllers
  m?: string;    // Additional Info
  d?: number;    // Die
  e?: number;    // CE
  r?: number;    // Rb
  n?: number;    // Channel
  p?: number;    // Plane
  ps?: number;   // Page Size
  bs?: number;   // Block Size
  ts?: number;   // Total Size
  ext?: Record<string, unknown>;  // Extra Info
}

export type VendorInfo = PartNumberInfo;

export type DatabaseInfo = {
  name: string;
  version: string;
  website: string;
  time: string;
  controllers: string[];
}

export interface Iddb {
  getFlashId(id: string): FlashIdInfo | null;
  getFlashIds(): Record<string, FlashIdInfo>;
}

export interface Vendor {
  getName(): string;
  getPartNumbers(): Record<string, VendorInfo>;
}

export interface FlashDatabase {
  info: DatabaseInfo;
  iddb: Iddb;
  micron?: Record<string, string>;
  getVendors(): Vendor[];
  getVendor(name: string): Vendor | null;
}
