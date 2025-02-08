import { AbstractDecoder } from './AbstractDecoder.js';
import type { FlashInfo } from '../types/FlashInfo.js';
import { Constants } from '../types/Constants.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';

export class MicronDecoder extends AbstractDecoder {
  public getName(): string {
    return Constants.VENDOR_MICRON;
  }

  public check(partNumber: string): boolean {
    return partNumber.startsWith('MT') && !partNumber.startsWith('MTF');
  }

  public decode(partNumber: string): FlashInfo {
    const info = new FlashInfoImpl();
    info.setVendor(this.getName());
    info.setPartNumber(partNumber);

    const parts = partNumber.split('-');
    if (parts.length < 2) return info;

    // Parse density and cell level
    const densityPart = parts[0].substring(2);
    if (densityPart.includes('G')) {
      info.setDensity(densityPart);
      const cellLevel = densityPart.charAt(densityPart.length - 2);
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
    }

    // Parse interface type
    const interfacePart = parts[1];
    if (interfacePart) {
      const iface = {
        toggle: interfacePart.includes('T'),
        async: interfacePart.includes('A'),
        sync: interfacePart.includes('S')
      };
      info.setInterface(iface);
    }

    // Parse voltage
    if (parts.length > 2) {
      const voltagePart = parts[2];
      if (voltagePart.startsWith('3')) {
        info.setVoltage('3.3V');
      } else if (voltagePart.startsWith('1')) {
        info.setVoltage('1.8V');
      }
    }

    return this.getFlashInfoFromFdb(info) || info;
  }

  public getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null {
    return info;
  }
}
