import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';
import { FlashDetector } from '../core/FlashDetector.js';

export class MicronFbgaCodeDecoder extends AbstractDecoder {
  constructor() {
    super('Micron', 'NAND', '20nm', 'MLC', '3.3V', { ce: 1, ch: 1, die: 1, rb: 1 });
  }

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
      const decodedInfo = FlashDetector.getInstance().decode(pns[0]);
      if (decodedInfo !== null) {
        decodedInfo.setPartNumber(partNumber);

        if (decodedInfo.getVendor() === Constants.VENDOR_MICRON) {
          const extra = decodedInfo.getExt();
          extra["micronPn"] = pns[0];

          if (i.length === 5) {
            const chars = i.split("");
            const year = chars.splice(0, 1).join("");
            const weekCode = chars.splice(0, 1).join("");
            const week = ((weekCode.charCodeAt(0) - 64) * 2).toString().padStart(2, '0');
            extra["productionDate"] = year + week;

            chars.splice(0, 1); // Skip one char
            
            const diffusion = chars.splice(0, 1).join("");
            const encapsulation = chars.splice(0, 1).join("");
            
            if (diffusion in MicronFbgaCodeDecoder.COUNTRY_CODE) {
              extra["diffusion"] = MicronFbgaCodeDecoder.COUNTRY_CODE[diffusion];
            }
            if (encapsulation in MicronFbgaCodeDecoder.COUNTRY_CODE) {
              extra["encapsulation"] = MicronFbgaCodeDecoder.COUNTRY_CODE[encapsulation];
            }
          }

          decodedInfo.setExt(extra);
        }
        return decodedInfo;
      }
    }

    return new FlashInfoImpl().setVendor(Constants.UNKNOWN);
  }

  public getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    const pn = info.getPartNumber();
    const pns = pn.split("-");
    if (pns.length === 2) {
      const decodedInfo = FlashDetector.getInstance().decode(pns[0]);
      if (decodedInfo !== null) {
        const extra = decodedInfo.getExt();
        const chars = pns[1].split("");

        if (chars.length >= 5) {
          const year = chars.splice(0, 1).join("");
          const weekCode = chars.splice(0, 1).join("");
          if (weekCode >= "1" && weekCode <= "9") {
            extra["week"] = weekCode;
          }
          chars.splice(0, 1); // Skip one char

          const diffusion = chars.splice(0, 1).join("");
          const encapsulation = chars.splice(0, 1).join("");

          if (diffusion in MicronFbgaCodeDecoder.COUNTRY_CODE) {
            extra["diffusion"] = MicronFbgaCodeDecoder.COUNTRY_CODE[diffusion];
          }
          if (encapsulation in MicronFbgaCodeDecoder.COUNTRY_CODE) {
            extra["encapsulation"] = MicronFbgaCodeDecoder.COUNTRY_CODE[encapsulation];
          }
        }

        return decodedInfo;
      }
    }
    return null;
  }
}
