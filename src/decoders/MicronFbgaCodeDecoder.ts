import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';
import { FlashDetector } from '../core/FlashDetector.js';

export class MicronFbgaCodeDecoder extends AbstractDecoder {
  private static readonly COUNTRY_CODE: Record<string, string> = {
    '1': Constants.USA,
    '2': Constants.SINGAPORE,
    '3': Constants.ITALY,
    '4': Constants.JAPAN,
    '5': Constants.CHINA,
    '7': Constants.TAIWAN,
    '8': Constants.KOREA,
    '9': Constants.MIXED,
    'B': Constants.ISRAEL,
    'C': Constants.IRELAND,
    'D': Constants.MALAYSIA,
    'F': Constants.PHILIPPINES
  };

  public getName(): string {
    return "MicronFBGACode";
  }

  public check(partNumber: string): boolean {
    const prefixes = ["NW", "NX", "NQ", "PF", "NY", "NC"];
    return prefixes.some(h => 
      partNumber.startsWith(h) || 
      (partNumber.length === 10 && partNumber.substring(5, 7) === h)
    );
  }

  public decode(partNumber: string): FlashInfo {
    let i = partNumber;
    let code = partNumber;
    if (partNumber.length === 10) {
      code = partNumber.substring(0, 5);
      i = partNumber.substring(5);
    }

    const pns = DatabaseManager.getInstance().searchMicronFbgaCode(code);
    if (pns && pns.length > 0) {
      const info = FlashDetector.detect(pns[0]);
      info.setPartNumber(partNumber);

      if (info.getVendor() === Constants.VENDOR_MICRON) {
        const extra = info.getExt();
        extra["micronPn"] = pns[0];

        if (i.length === 5) {
          const year = AbstractDecoder.shiftChars(i, 1);
          const weekCode = AbstractDecoder.shiftChars(i, 1);
          const week = ((weekCode.charCodeAt(0) - 64) * 2).toString().padStart(2, '0');
          extra["productionDate"] = year + week;

          AbstractDecoder.shiftChars(i, 1); // Skip one char
          
          const diffusion = AbstractDecoder.shiftChars(i, 1);
          const encapsulation = AbstractDecoder.shiftChars(i, 1);
          
          extra["diffusion"] = AbstractDecoder.getOrDefault(diffusion, MicronFbgaCodeDecoder.COUNTRY_CODE);
          extra["encapsulation"] = AbstractDecoder.getOrDefault(encapsulation, MicronFbgaCodeDecoder.COUNTRY_CODE);
        }

        info.setExt(extra);
      }
      return info;
    }

    return new FlashInfoImpl().setVendor(Constants.UNKNOWN);
  }

  protected getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return null;
  }
}
