import type { FlashIdInfo } from './FlashIdInfo.js';

export interface PartNumberInfo {
  getPartNumber(): string;
  getFlashIds(): string[];
  getProcessNode(): string;
  getCellLevel(): string;
  getControllers(): string[];
  getRemark(): string;
  getDie(): number;
  getCe(): number;
  getRb(): number;
  getCh(): number;
  toJSON(): any;
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
  getFlashId(id: string, create?: boolean): FlashIdInfo;
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
  toJSON(): any;
}
