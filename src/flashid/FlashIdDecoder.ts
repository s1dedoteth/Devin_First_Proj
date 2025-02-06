import { FlashIdInfo, FlashIdInfoImpl } from '../types/FlashIdInfo.js';

import { IdRule, IdRules, IdDefinition } from '../types/IdDefinition.js';

export abstract class FlashIdDecoder {
  protected vendorName: string;
  protected vendorId: number;
  protected def: IdDefinition;

  constructor(vendorName: string, vendorId: number, def: Record<string, IdRules>) {
    this.vendorName = vendorName;
    this.vendorId = vendorId;
    this.def = def;
  }

  public check(id: number): boolean {
    if ((id > 0x100000000000 && id < 0x1000000000000) && (id >> 40) === this.vendorId) {
      return true;
    }
    return false;
  }

  public decode(id: number): FlashIdInfo {
    return this.decodeIdDef(id, this.def, new FlashIdInfoImpl(id).setVendor(this.vendorName));
  }

  protected static getByte(id: number, offset: number): number {
    return (id >> (8 * (6 - offset))) & 0xff;
  }

  protected decodeIdDef(id: number, def: IdDefinition, info: FlashIdInfo): FlashIdInfo {
    const ext: Record<string, string> = {};
    for (const [offsetStr, rules] of Object.entries(def)) {
      const offset = parseInt(offsetStr);
      const byte = FlashIdDecoder.getByte(id, offset);
      for (const [name, rule] of Object.entries(rules)) {
        const typedRule = rule as IdRule;
        let data = 0;
        for (const dq of typedRule.dq) {
          data = (data << 1) + ((byte >> dq) & 0b1);
        }
        const value = typedRule.def[data];
        if (value !== undefined) {
          if (name.startsWith('ext:')) {
            ext[name.split(':')[1]] = String(value);
          } else {
            const methodName = 'set' + name.charAt(0).toUpperCase() + name.slice(1);
            if (typeof (info as any)[methodName] === 'function') {
              (info as any)[methodName](value);
            }
          }
        }
      }
    }
    return info.setExt(ext);
  }

  protected static checkProperties(...props: any[]): boolean {
    for (const prop of props) {
      if (prop === null || prop === undefined) {
        return false;
      }
      if (typeof prop === 'number' && prop <= 0) {
        return false;
      }
      if (typeof prop === 'string' && prop.trim().length === 0) {
        return false;
      }
    }
    return true;
  }
}
