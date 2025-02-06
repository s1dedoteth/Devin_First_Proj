import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

export class PhisonDecoder extends AbstractDecoder {
  public getName(): string {
    return 'Phison';
  }

  public check(partNumber: string): boolean {
    return partNumber.startsWith('PS');
  }

  public decode(partNumber: string): FlashInfo {
    const info = new FlashInfoImpl();
    info.setVendor(this.getName());
    info.setPartNumber(partNumber);

    // Parse cell level
    if (partNumber.includes('SLC')) {
      info.setCellLevel('SLC');
    } else if (partNumber.includes('MLC')) {
      info.setCellLevel('MLC');
    } else if (partNumber.includes('TLC')) {
      info.setCellLevel('TLC');
    } else if (partNumber.includes('QLC')) {
      info.setCellLevel('QLC');
    }

    // Parse density
    const densityMatch = partNumber.match(/(\d+)G/);
    if (densityMatch) {
      info.setDensity(`${densityMatch[1]}Gb`);
    }

    // Parse interface
    const iface = {
      toggle: partNumber.includes('T'),
      async: partNumber.includes('A'),
      sync: partNumber.includes('S')
    };
    info.setInterface(iface);

    // Parse voltage
    if (partNumber.includes('1.8V')) {
      info.setVoltage('1.8V');
    } else if (partNumber.includes('3.3V')) {
      info.setVoltage('3.3V');
    }

    return this.getFlashInfoFromFdb(info) || info;
  }

  public getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return this.getFlashInfoFromFdbImpl(info);
  }
}
