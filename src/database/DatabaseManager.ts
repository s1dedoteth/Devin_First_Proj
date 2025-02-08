import type { FlashDatabase, DatabaseInfo, Iddb, Vendor, VendorInfo } from '../types/Database.js';
import { PartNumberInfoImpl } from './PartNumberInfoImpl.js';
import type { FlashIdInfo } from '../types/FlashIdInfo.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

export class DatabaseManager {
  private static instance: DatabaseManager;
  private database: FlashDatabase | null = null;

  private constructor() {}

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  public async loadDatabase(path: string): Promise<void> {
    try {
      const response = await fetch(path);
      this.database = await response.json() as FlashDatabase;
    } catch (error) {
      console.error('Failed to load database:', error);
      throw error;
    }
  }

  public getDatabaseInfo(): DatabaseInfo {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    return this.database.info;
  }

  public getFlashId(id: string): FlashIdInfo | null {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    return this.database.iddb.getFlashId(id);
  }

  public getFlashIds(): Record<string, FlashIdInfo> {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    return this.database.iddb.getFlashIds();
  }

  public getVendors(): Vendor[] {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    return this.database.getVendors();
  }

  public getVendor(name: string): Vendor | null {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    return this.database.getVendor(name);
  }

  public getVendorInfo(vendor: string, partNumber: string): VendorInfo | null {
    if (!this.database) {
      throw new Error('Database not loaded');
    }
    const v = this.database.getVendor(vendor);
    if (!v) return null;
    
    const partNumbers = v.getPartNumbers();
    const info = partNumbers[partNumber];
    return info ? new PartNumberInfoImpl(partNumber, info) : null;
  }

  public getPartNumber(vendor: string, partNumber: string): FlashInfo | null {
    const info = this.getVendorInfo(vendor, partNumber);
    if (!info) return null;

    const flashInfo = new FlashInfoImpl();
    flashInfo.setPartNumber(partNumber)
      .setVendor(vendor)
      .setType(Constants.UNKNOWN)
      .setDensity(Constants.UNKNOWN)
      .setDeviceWidth(0)
      .setCellLevel(info.getCellLevel())
      .setProcessNode(info.getProcessNode())
      .setGeneration(Constants.UNKNOWN)
      .setInterface({
        toggle: false,
        async: false,
        sync: false
      })
      .setClassification({
        ce: info.getCe(),
        ch: info.getCh(),
        die: info.getDie(),
        rb: info.getRb()
      })
      .setVoltage(Constants.UNKNOWN)
      .setPackage(Constants.UNKNOWN)
      .setController(info.getControllers())
      .setRemark(info.getRemark())
      .setExt({})
      .setFlashId(info.getFlashIds());
    return flashInfo;
  }

  public searchMicronFbgaCode(fbgaCode: string): string | null {
    if (!this.database?.micron) {
      return null;
    }
    return this.database.micron[fbgaCode] || null;
  }

  public searchPartNumber(pn: string, partMatch: boolean = false, limit: number = 0): Record<string, FlashInfo> {
    const results: Record<string, FlashInfo> = {};
    if (!this.database) {
      return results;
    }

    const vendors = this.database.getVendors();
    for (const vendor of vendors) {
      const partNumbers = vendor.getPartNumbers();
      for (const [partNumber, rawInfo] of Object.entries(partNumbers)) {
        if (partMatch ? partNumber.includes(pn) : partNumber === pn) {
          const info = new PartNumberInfoImpl(partNumber, rawInfo);
          const flashInfo = new FlashInfoImpl();
          flashInfo.setPartNumber(partNumber)
            .setVendor(vendor.getName())
            .setType(Constants.UNKNOWN)
            .setDensity(Constants.UNKNOWN)
            .setDeviceWidth(0)
            .setCellLevel(info.getCellLevel())
            .setProcessNode(info.getProcessNode())
            .setGeneration(Constants.UNKNOWN)
            .setInterface({
              toggle: false,
              async: false,
              sync: false
            })
            .setClassification({
              ce: info.getCe(),
              ch: info.getCh(),
              die: info.getDie(),
              rb: info.getRb()
            })
            .setVoltage(Constants.UNKNOWN)
            .setPackage(Constants.UNKNOWN)
            .setController(info.getControllers())
            .setRemark(info.getRemark())
            .setExt({})
            .setFlashId(info.getFlashIds());
          results[partNumber] = flashInfo;

          if (limit > 0 && Object.keys(results).length >= limit) {
            return results;
          }
        }
      }
    }

    return results;
  }

  public searchFlashId(id: string, partMatch: boolean = false, limit: number = 0): Record<string, FlashIdInfo> {
    const results: Record<string, FlashIdInfo> = {};
    if (!this.database) {
      return results;
    }

    const flashIds = this.database.iddb.getFlashIds();
    for (const [flashId, info] of Object.entries(flashIds)) {
      if (partMatch ? flashId.includes(id) : flashId === id) {
        results[flashId] = info;

        if (limit > 0 && Object.keys(results).length >= limit) {
          return results;
        }
      }
    }

    return results;
  }

  public getSummary(pn: string, lang: string | null = null): string {
    return `Part Number: ${pn}`;
  }

  public getIdSummary(id: string, lang: string | null = null): string {
    return `Flash ID: ${id}`;
  }
}
