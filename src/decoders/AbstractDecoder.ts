import { FlashInfo } from '../types/FlashInfo.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';
import { Constants } from '../types/Constants.js';
import { PartNumberInfo } from '../types/Database.js';

export abstract class AbstractDecoder {
  public abstract check(pn: string): boolean;

  protected constructor(
    protected readonly vendor: string,
    protected readonly type: string,
    protected readonly processNode: string,
    protected readonly cellLevel: string,
    protected readonly voltage: string,
    protected readonly classification: {
      ce: number;
      ch: number;
      die: number;
      rb: number;
    }
  ) {}

  public decode(pn: string): FlashInfo {
    const info = new FlashInfoImpl();
    info.setPartNumber(pn)
      .setVendor(this.vendor)
      .setType(this.type)
      .setDensity(Constants.UNKNOWN)
      .setDeviceWidth(0)
      .setCellLevel(this.cellLevel)
      .setProcessNode(this.processNode)
      .setVoltage(this.voltage)
      .setInterface({
        async: false,
        sync: false,
        toggle: false
      })
      .setClassification(this.classification)
      .setController([])
      .setRemark('')
      .setExt({});

    return info;
  }

  public getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return info;
  }

  protected static shiftChars(str: string[], count: number): string {
    return str.splice(0, count).join('');
  }

  protected static getOrDefault<T>(value: T | undefined, defaultValue: T): T {
    return value ?? defaultValue;
  }
}
