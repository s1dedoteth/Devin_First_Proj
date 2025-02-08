import { DensityUnit } from './Constants.js';
import { FlashInfo } from './FlashInfo.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

export interface FlashIdInfo {
  getType(): string;
  setType(type: string): this;
  getVendor(): string;
  setVendor(vendor: string): this;
  getCellLevel(): string;
  setCellLevel(cellLevel: string): this;
  getDensity(): string;
  setDensity(density: string | DensityUnit): this;
  getProcessNode(): string;
  setProcessNode(processNode: string): this;
  getVoltage(): string;
  setVoltage(voltage: string): this;
  getExt(): Record<string, any>;
  setExt(ext: Record<string, any>): this;
  setPlane(plane: string): this;
  setDie(die: string): this;
  setPageSize(pageSize: string): this;
  setBlockSize(blockSize: string | null): this;
  setControllers(controllers: string[]): this;
  setPartNumbers(partNumbers: string[]): this;
  setId(id: string): this;
  toFlashInfo(): FlashInfo;
}

// Implementation moved to FlashIdInfoImpl.ts
