import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

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
    return Constants.VENDOR_MICRON;
  }

  public check(partNumber: string): boolean {
    if (partNumber.length < 2) return false;
    const prefix = partNumber.substring(0, 2);
    return ['NW', 'NX', 'NQ', 'PF', 'NY', 'NC'].includes(prefix);
  }

  decode(partNumber: string): FlashInfo {
    const info = new FlashInfoImpl();
    info.setVendor(this.getName());

    // Extract FBGA code
    const fbgaCode = partNumber.substring(0, 5);
    const micronPn = DatabaseManager.getInstance().searchMicronFbgaCode(fbgaCode);
    if (micronPn) {
      info.setPartNumber(micronPn);
    }

    // Extract date code if length is 10
    if (partNumber.length === 10) {
      const dateCode = partNumber.substring(5, 7);
      const diffusion = partNumber.charAt(7);
      const encapsulation = partNumber.charAt(8);

      // Parse production date
      const year = dateCode.charCodeAt(0) - 64;
      const week = (dateCode.charCodeAt(1) - 64) * 2;
      info.setProductionDate(`20${year} Week ${week}`);

      // Map country codes
      const diffusionLocation = MicronFbgaCodeDecoder.COUNTRY_CODE[diffusion] ?? Constants.UNKNOWN;
      const encapsulationLocation = MicronFbgaCodeDecoder.COUNTRY_CODE[encapsulation] ?? Constants.UNKNOWN;

      info.setExt({
        [Constants.DIFFUSION]: diffusionLocation,
        [Constants.ENCAPSULATION]: encapsulationLocation,
        [Constants.MICRON_PN]: micronPn ?? Constants.UNKNOWN
      });
    }

    return info;
  }

  getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return this.getFlashInfoFromFdbImpl(info);
  }
}
