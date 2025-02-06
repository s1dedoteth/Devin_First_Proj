import { DatabaseManager } from '../database/DatabaseManager';
import { ProcessorManager } from '../processors/ProcessorManager';
import type { FlashInfo } from '../types/FlashInfo';
import type { FlashIdInfo } from '../types/FlashIdInfo';
import type { FlashIdInfoExtended } from '../types/FlashIdInfoExtended';
import { FlashIdInfoExtendedImpl } from '../flashid/FlashIdInfoExtendedImpl';
import { AbstractDecoder } from '../decoders/AbstractDecoder';
import { Constants } from '../types/Constants';
import { MicronDecoder } from '../decoders/MicronDecoder';
import { SKHynix3DDecoder } from '../decoders/SKHynix3DDecoder';
import { SKHynixDecoder } from '../decoders/SKHynixDecoder';
import { SKHynixLegacyDecoder } from '../decoders/SKHynixLegacyDecoder';
import { SamsungDecoder } from '../decoders/SamsungDecoder';
import { IntelDecoder } from '../decoders/IntelDecoder';
import { MicronFbgaCodeDecoder } from '../decoders/MicronFbgaCodeDecoder';
import { SpecTekDecoder } from '../decoders/SpecTekDecoder';
import { WesternDigitalDecoder } from '../decoders/WesternDigitalDecoder';
import { WesternDigitalShortCodeDecoder } from '../decoders/WesternDigitalShortCodeDecoder';
import { YangtzeDecoder } from '../decoders/YangtzeDecoder';
import { PhisonDecoder } from '../decoders/PhisonDecoder';
import { KioxiaDecoder } from '../decoders/KioxiaDecoder';

export class FlashDetector {
  private static decoders: AbstractDecoder[] = [];
  private static db = DatabaseManager.getInstance();
  private static processors = ProcessorManager.getInstance();

  public static initialize(): void {
    this.registerDecoder(new MicronDecoder());
    this.registerDecoder(new SKHynix3DDecoder());
    this.registerDecoder(new SKHynixDecoder());
    this.registerDecoder(new SKHynixLegacyDecoder());
    this.registerDecoder(new SamsungDecoder());
    this.registerDecoder(new IntelDecoder());
    this.registerDecoder(new MicronFbgaCodeDecoder());
    this.registerDecoder(new SpecTekDecoder());
    this.registerDecoder(new WesternDigitalDecoder());
    this.registerDecoder(new WesternDigitalShortCodeDecoder());
    this.registerDecoder(new YangtzeDecoder());
    this.registerDecoder(new PhisonDecoder());
    this.registerDecoder(new KioxiaDecoder());
  }

  public static registerDecoder(decoder: AbstractDecoder): void {
    this.decoders.push(decoder);
  }

  public static detect(partNumber: string): FlashInfo {
    const cleanPn = partNumber.replace(/[ ,&.|]/g, '').toUpperCase();
    
    for (const decoder of this.decoders) {
      if (decoder.check(cleanPn)) {
        const info = decoder.decode(cleanPn);
        return this.processors.processFlashInfo(info);
      }
    }

    return this.processors.processFlashInfo({
      partNumber: cleanPn,
      vendor: Constants.UNKNOWN,
      type: Constants.UNKNOWN,
      density: Constants.UNKNOWN,
      deviceWidth: 0,
      cellLevel: Constants.UNKNOWN,
      processNode: Constants.UNKNOWN,
      generation: Constants.UNKNOWN,
      interface: {
        toggle: false,
        async: false,
        sync: false
      },
      classification: {
        ce: Constants.UNKNOWN_PROP,
        ch: Constants.UNKNOWN_PROP,
        die: Constants.UNKNOWN_PROP,
        rb: Constants.UNKNOWN_PROP
      },
      voltage: Constants.UNKNOWN,
      package: Constants.UNKNOWN,
      controller: [],
      remark: '',
      extraInfo: {},
      flashId: []
    });
  }

  public static decodeFlashId(id: string): FlashIdInfoExtended {
    const cleanId = id.toUpperCase().padEnd(12, '0');
    const flashId = this.db.getFlashId(cleanId);
    
    const info = new FlashIdInfoExtendedImpl(parseInt(cleanId, 16));
    info.setId(cleanId)
        .setVendor(this.getVendorFromId(cleanId))
        .setCellLevel(this.getCellLevelFromId(cleanId))
        .setDensity(this.getDensityFromId(cleanId))
        .setProcessNode(this.getProcessNodeFromId(cleanId))
        .setVoltage(this.getVoltageFromId(cleanId))
        .setExt({});

    if (flashId) {
      info.s = flashId.s;
      info.p = flashId.p;
      info.b = flashId.b;
      info.t = flashId.t;
      info.n = flashId.n;
      info.setDie(flashId.s)
          .setPlane(flashId.p)
          .setPageSize(flashId.s)
          .setBlockSize(flashId.b)
          .setControllers(flashId.t)
          .setPartNumbers(flashId.n);
    } else {
      info.s = -1;
      info.p = -1;
      info.b = -1;
      info.t = [];
      info.n = [];
      info.setDie(Constants.UNKNOWN_PROP)
          .setPlane(Constants.UNKNOWN_PROP)
          .setPageSize(Constants.UNKNOWN_PROP)
          .setBlockSize(Constants.UNKNOWN_PROP)
          .setControllers([])
          .setPartNumbers([]);
    }

    return info;
  }

  private static getVendorFromId(id: string): string {
    const firstByte = parseInt(id.substring(0, 2), 16);
    switch (firstByte) {
      case 0x98: return 'Kioxia';
      case 0x45: return 'Western Digital';
      case 0x9B: return 'YMTC';
      case 0x89: return 'Intel';
      case 0x2C: return 'Micron';
      case 0x01: return 'SpecTek';
      case 0xEC: return 'Samsung';
      case 0xAD: return 'SK Hynix';
      default: return Constants.UNKNOWN;
    }
  }

  private static getCellLevelFromId(id: string): string {
    const thirdByte = parseInt(id.substring(4, 6), 16);
    const cellType = (thirdByte >> 2) & 0x3;
    switch (cellType) {
      case 0: return 'SLC';
      case 1: return 'MLC';
      case 2: return 'TLC';
      case 3: return 'QLC';
      default: return Constants.UNKNOWN;
    }
  }

  private static getDensityFromId(id: string): string {
    const fourthByte = parseInt(id.substring(6, 8), 16);
    return `${1 << (fourthByte - 10)}Gb`;
  }

  private static getProcessNodeFromId(id: string): string {
    const fifthByte = parseInt(id.substring(8, 10), 16);
    return `${((fifthByte >> 4) & 0xF) * 10}nm`;
  }

  private static getVoltageFromId(id: string): string {
    const thirdByte = parseInt(id.substring(4, 6), 16);
    return (thirdByte & 0x1) === 0 ? '3.3V' : '1.8V';
  }
}
