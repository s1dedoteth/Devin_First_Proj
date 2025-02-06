import { FlashInfo } from '../types/FlashInfo.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { IdDb } from './IdDb.js';
import { Logger } from '../utils/Logger.js';

export interface FdbInfo {
  name: string;
  website: string;
  version: string;
  time: string;
  controllers: string[];
}

export interface FdbData {
  info: FdbInfo;
  iddb: Record<string, any>;
}

export class Fdb {
  private info: FdbInfo;
  private iddb: Record<string, any>;
  private vendors: Map<string, VendorInfo>;

  constructor(data: FdbData) {
    this.info = data.info;
    this.iddb = data.iddb;
    this.vendors = new Map();
  }

  public getIddb(): IdDb {
    return new IdDb();
  }

  public getVendors(): VendorInfo[] {
    return Array.from(this.vendors.values());
  }

  public mergeFlashData(data: any): void {
    // Merge flash data from JSON
    if (data.info) {
      this.info.controllers = [...new Set([...this.info.controllers, ...data.info.controllers])];
    }

    if (data.iddb) {
      for (const [id, info] of Object.entries(data.iddb)) {
        if (!this.iddb[id]) {
          this.iddb[id] = info;
        } else {
          // Merge flash ID info
          const existing = this.iddb[id];
          existing.pn = [...new Set([...existing.pn, ...(info as any).pn])];
        }
      }
    }

    if (data.vendors) {
      for (const [vendor, info] of Object.entries(data.vendors)) {
        if (!this.vendors.has(vendor)) {
          this.vendors.set(vendor, new VendorInfo(vendor, info as any));
        } else {
          this.vendors.get(vendor)!.merge(info as any);
        }
      }
    }
  }

  public toJSON(): Record<string, any> {
    return {
      info: this.info,
      iddb: this.iddb,
      vendors: Object.fromEntries(Array.from(this.vendors.entries()).map(([k, v]) => [k, v.toJSON()]))
    };
  }
}

export class VendorInfo {
  private name: string;
  private partNumbers: Map<string, PartNumberInfo>;

  constructor(name: string, data: any) {
    this.name = name;
    this.partNumbers = new Map();
    if (data.pn) {
      for (const [pn, info] of Object.entries(data.pn)) {
        this.partNumbers.set(pn, new PartNumberInfo(pn, info as any));
      }
    }
  }

  public getName(): string {
    return this.name;
  }

  public getPartNumbers(): PartNumberInfo[] {
    return Array.from(this.partNumbers.values());
  }

  public merge(data: any): void {
    if (data.pn) {
      for (const [pn, info] of Object.entries(data.pn)) {
        if (!this.partNumbers.has(pn)) {
          this.partNumbers.set(pn, new PartNumberInfo(pn, info as any));
        } else {
          this.partNumbers.get(pn)!.merge(info as any);
        }
      }
    }
  }

  public toJSON(): Record<string, any> {
    return {
      pn: Object.fromEntries(Array.from(this.partNumbers.entries()).map(([k, v]) => [k, v.toJSON()]))
    };
  }
}

export class PartNumberInfo {
  private partNumber: string;
  private flashIds: string[];
  private info: Record<string, any>;

  constructor(partNumber: string, data: any) {
    this.partNumber = partNumber;
    this.flashIds = data.id || [];
    this.info = data.info || {};
  }

  public getPartNumber(): string {
    return this.partNumber;
  }

  public getFlashIds(): string[] {
    return this.flashIds;
  }

  public merge(data: any): void {
    if (data.id) {
      this.flashIds = [...new Set([...this.flashIds, ...data.id])];
    }
    if (data.info) {
      Object.assign(this.info, data.info);
    }
  }

  public toJSON(): Record<string, any> {
    return {
      id: this.flashIds,
      info: this.info
    };
  }
}
