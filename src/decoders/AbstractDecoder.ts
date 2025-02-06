import { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import { Logger } from '../utils/Logger.js';

export abstract class AbstractDecoder {
  protected static readonly CELL_LEVEL: Record<number, string | null> = {
    [-1]: null,
    1: "SLC",
    2: "MLC",
    3: "TLC",
    4: "QLC"
  };

  public abstract getName(): string;
  public abstract check(partNumber: string): boolean;
  public abstract decode(partNumber: string): FlashInfo;

  protected static shiftChars(str: string, num: number): string {
    if (num > str.length) {
      return "";
    }
    const res = str.substring(0, num);
    str = str.substring(num);
    return res;
  }

  protected static getOrDefault<T>(str: string | number, info: Record<string | number, T>, defaultValue: T = Constants.UNKNOWN as T): T {
    return info[str] ?? defaultValue;
  }

  protected static matchFromStart(str: string, info: Record<string, string>, defaultValue: string = Constants.UNKNOWN): string {
    const level: Record<number, Record<string, string>> = {};
    
    for (const [k, v] of Object.entries(info)) {
      const len = k.length;
      if (level[len]) {
        level[len][k] = v;
      } else {
        level[len] = { [k]: v };
      }
    }

    const lengths = Object.keys(level).map(Number).sort((a, b) => b - a);

    for (const len of lengths) {
      const patterns = level[len];
      for (const [k, v] of Object.entries(patterns)) {
        if (str.startsWith(k)) {
          str = str.substring(k.length);
          return v;
        }
      }
    }

    return defaultValue;
  }

  protected getFlashInfoFromFdbImpl(info: FlashInfo): FlashInfo | null {
    const dbManager = DatabaseManager.getInstance();
    const dbInfo = dbManager.getVendorInfo(info.getVendor(), info.getPartNumber());
    if (!dbInfo) return null;

    info.setType(Constants.UNKNOWN)
        .setDensity(Constants.UNKNOWN)
        .setDeviceWidth(0)
        .setCellLevel(dbInfo.c)
        .setProcessNode(dbInfo.l)
        .setGeneration(Constants.UNKNOWN)
        .setInterface({
          toggle: false,
          async: false,
          sync: false
        })
        .setClassification({
          ce: dbInfo.e,
          ch: dbInfo.n,
          die: dbInfo.d,
          rb: dbInfo.r
        })
        .setVoltage(Constants.UNKNOWN)
        .setPackage(Constants.UNKNOWN)
        .setController(dbInfo.t)
        .setRemark(dbInfo.m)
        .setFlashId(dbInfo.id);

    return info;
  }
}
