import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

export class WesternDigitalShortCodeDecoder extends AbstractDecoder {
  public getName(): string {
    return 'Western Digital';
  }

  public check(partNumber: string): boolean {
    return partNumber.startsWith('SD') && partNumber.length === 8;
  }

  public decode(partNumber: string): FlashInfo {
    const info = new FlashInfoImpl();
    info.setVendor(this.getName());
    info.setPartNumber(partNumber);

    // Parse cell level from 3rd character
    const cellLevel = partNumber.charAt(2);
    switch (cellLevel) {
      case 'L':
        info.setCellLevel('SLC');
        break;
      case 'M':
        info.setCellLevel('MLC');
        break;
      case 'T':
        info.setCellLevel('TLC');
        break;
      case 'Q':
        info.setCellLevel('QLC');
        break;
    }

    // Parse density from characters 4-5
    const density = parseInt(partNumber.substring(3, 5), 16);
    if (!isNaN(density)) {
      info.setDensity(`${1 << (density - 10)}Gb`);
    }

    // Parse interface from 6th character
    const interfaceType = partNumber.charAt(5);
    const iface = {
      toggle: interfaceType === 'T',
      async: interfaceType === 'A',
      sync: interfaceType === 'S'
    };
    info.setInterface(iface);

    // Parse voltage from 7th character
    const voltage = partNumber.charAt(6);
    if (voltage === '3') {
      info.setVoltage('3.3V');
    } else if (voltage === '1') {
      info.setVoltage('1.8V');
    }

    return this.getFlashInfoFromFdb(info) || info;
  }

  public getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return this.getFlashInfoFromFdbImpl(info);
  }
}
