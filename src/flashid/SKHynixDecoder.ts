import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from './FlashIdInfo.js';
import { Constants } from '../types/Constants.js';

export class SKHynixDecoder extends FlashIdDecoder {
  public check(id: number): boolean {
    return (id >> 24) === 0xAD;
  }

  public decode(id: number): FlashIdInfo {
    const info = new FlashIdInfo(id);
    info.setVendor('SK Hynix');

    const thirdByte = (id >> 16) & 0xFF;
    const cellType = (thirdByte >> 2) & 0x3;
    switch (cellType) {
      case 0:
        info.setCellLevel('SLC');
        break;
      case 1:
        info.setCellLevel('MLC');
        break;
      case 2:
        info.setCellLevel('TLC');
        break;
      case 3:
        info.setCellLevel('QLC');
        break;
      default:
        info.setCellLevel(Constants.UNKNOWN);
    }

    const fourthByte = (id >> 8) & 0xFF;
    info.setDensity(`${1 << (fourthByte - 10)}Gb`);

    const fifthByte = id & 0xFF;
    info.setProcessNode(`${((fifthByte >> 4) & 0xF) * 10}nm`);

    info.setVoltage((thirdByte & 0x1) === 0 ? '3.3V' : '1.8V');

    return info;
  }
}
