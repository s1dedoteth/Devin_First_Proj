import type { FlashInfo } from '../types/FlashInfo.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import type { VendorInfo } from '../types/Database.js';
import type { Classification } from '../types/Classification.js';
import type { FlashInterface } from '../types/FlashInterface.js';
import { Constants } from '../types/Constants.js';

import type { Decoder } from '../types/Decoder.js';

export abstract class AbstractDecoder implements Decoder {
  protected static db: DatabaseManager = DatabaseManager.getInstance();

  abstract getName(): string;
  abstract check(partNumber: string): boolean;
  abstract decode(partNumber: string): FlashInfo;
  abstract getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null;

  protected getFlashInfoFromFdbImpl(info: FlashInfo): FlashInfo | null {
    const vendorInfo = AbstractDecoder.db.getVendorInfo(this.getName(), info.partNumber);
    if (!vendorInfo) return null;

    info.flashId = vendorInfo.id;
    info.controller = vendorInfo.t;
    if (vendorInfo.l && (info.processNode === Constants.UNKNOWN || !info.processNode)) {
      info.processNode = vendorInfo.l;
    }
    info.remark = vendorInfo.m;
    if (!info.cellLevel && vendorInfo.c) {
      info.cellLevel = vendorInfo.c;
    }

    const classification = info.classification || {} as Classification;
    if (vendorInfo.d !== Constants.UNKNOWN_PROP) {
      classification.die = vendorInfo.d;
    }
    if (vendorInfo.e !== Constants.UNKNOWN_PROP) {
      classification.ce = vendorInfo.e;
    }
    if (vendorInfo.r !== Constants.UNKNOWN_PROP) {
      classification.rb = vendorInfo.r;
    }
    if (vendorInfo.n !== Constants.UNKNOWN_PROP) {
      classification.ch = vendorInfo.n;
    }
    info.classification = classification;

    return info;
  }

  protected createDefaultFlashInfo(partNumber: string): FlashInfo {
    return {
      partNumber,
      vendor: this.getName(),
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
      } as FlashInterface,
      classification: {
        ce: Constants.UNKNOWN_PROP,
        ch: Constants.UNKNOWN_PROP,
        die: Constants.UNKNOWN_PROP,
        rb: Constants.UNKNOWN_PROP
      } as Classification,
      voltage: Constants.UNKNOWN,
      package: Constants.UNKNOWN,
      controller: [],
      remark: '',
      extraInfo: {},
      flashId: []
    };
  }

  protected shiftChars(partNumber: string, count: number): string {
    return partNumber.substring(0, count);
  }
}
