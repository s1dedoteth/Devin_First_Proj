import type { FlashIdInfo, FlashIdInfoRaw } from './FlashIdInfo.js';

export type VendorInfo = {
  id: string[];  // Flash Id
  l: string;  // Process node
  c: string;  // Cell level
  t: string[];  // Controllers
  m: string;  // Additional Info
  d: number;  // Die
  e: number;  // CE
  r: number;  // Rb
  n: number;  // Channel
}

export type DatabaseInfo = {
  name: string;
  version: string;
  website: string;
  time: string;
  controllers: string[];
}

export interface Iddb {
  getFlashId(id: string): FlashIdInfoRaw | null;
  getFlashIds(): Record<string, FlashIdInfoRaw>;
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
