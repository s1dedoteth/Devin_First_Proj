import { AbstractDecoder } from '../decoders/AbstractDecoder.js';
import { MicronDecoder } from '../decoders/MicronDecoder.js';
import { SKHynix3DDecoder } from '../decoders/SKHynix3DDecoder.js';
import { SKHynixDecoder } from '../decoders/SKHynixDecoder.js';
import { SKHynixLegacyDecoder } from '../decoders/SKHynixLegacyDecoder.js';
import { SamsungDecoder } from '../decoders/SamsungDecoder.js';
import { IntelDecoder } from '../decoders/IntelDecoder.js';
import { MicronFbgaCodeDecoder } from '../decoders/MicronFbgaCodeDecoder.js';
import { SpecTekDecoder } from '../decoders/SpecTekDecoder.js';
import { WesternDigitalDecoder } from '../decoders/WesternDigitalDecoder.js';
import { WesternDigitalShortCodeDecoder } from '../decoders/WesternDigitalShortCodeDecoder.js';
import { YangtzeDecoder } from '../decoders/YangtzeDecoder.js';
import { PhisonDecoder } from '../decoders/PhisonDecoder.js';
import { KioxiaDecoder } from '../decoders/KioxiaDecoder.js';
import { FlashInfo } from '../types/FlashInfo.js';
import { DatabaseManager } from '../database/DatabaseManager.js';

export class FlashDetector {
  private static instance: FlashDetector;
  private decoders: AbstractDecoder[] = [];
  private dbManager: DatabaseManager;

  private constructor() {
    this.dbManager = DatabaseManager.getInstance();
    this.registerDecoders();
  }

  public static getInstance(): FlashDetector {
    if (!FlashDetector.instance) {
      FlashDetector.instance = new FlashDetector();
    }
    return FlashDetector.instance;
  }

  public static initialize(): void {
    FlashDetector.getInstance();
  }

  public static detect(pn: string): FlashInfo | null {
    return FlashDetector.getInstance().decode(pn);
  }

  public static decodeFlashId(id: string): FlashInfo | null {
    return FlashDetector.getInstance().decodeId(id);
  }

  private registerDecoders(): void {
    this.decoders = [
      new MicronDecoder(),
      new SKHynix3DDecoder(),
      new SKHynixDecoder(),
      new SKHynixLegacyDecoder(),
      new SamsungDecoder(),
      new IntelDecoder(),
      new MicronFbgaCodeDecoder(),
      new SpecTekDecoder(),
      new WesternDigitalDecoder(),
      new WesternDigitalShortCodeDecoder(),
      new YangtzeDecoder(),
      new PhisonDecoder(),
      new KioxiaDecoder()
    ];
  }

  public decode(pn: string): FlashInfo | null {
    const cleanPn = pn.trim().toUpperCase();
    for (const decoder of this.decoders) {
      if (decoder.check(cleanPn)) {
        const info = decoder.decode(cleanPn);
        return decoder.getFlashInfoFromFdb(info);
      }
    }
    return null;
  }

  public decodeId(id: string): FlashInfo | null {
    const cleanId = id.trim().toUpperCase();
    const info = this.dbManager.getFlashId(cleanId);
    return info ? info.toFlashInfo() : null;
  }
}
