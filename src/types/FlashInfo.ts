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
  extraInfo: Record<string, any>;
  flashId: string[];
  productionDate?: string;

  getVendor(): string;
  getPartNumber(): string;
  setPartNumber(partNumber: string): this;
  setVendor(vendor: string): this;
  getExt(): Record<string, any>;
  setExt(ext: Record<string, any>): this;
  setType(type: string): this;
  setDensity(density: string): this;
  setDeviceWidth(deviceWidth: number): this;
  setCellLevel(cellLevel: string): this;
  setProcessNode(processNode: string): this;
  setGeneration(generation: string): this;
  setInterface(iface: FlashInterface): this;
  setClassification(classification: Classification): this;
  setVoltage(voltage: string): this;
  setPackage(pkg: string): this;
  setController(controller: string[]): this;
  setRemark(remark: string): this;
  setFlashId(flashId: string[]): this;
  setProductionDate(date: string): this;
}
