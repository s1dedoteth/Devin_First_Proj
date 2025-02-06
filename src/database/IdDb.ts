import { FlashIdInfo } from '../types/FlashIdInfo.js';

export interface IdDbEntry {
  pn: string[];
  info: Record<string, any>;
}

export class IdDb {
  private entries: Map<string, IdDbEntry>;

  constructor() {
    this.entries = new Map();
  }

  public getFlashId(id: string, create: boolean = false): IdDb {
    if (!this.entries.has(id) && create) {
      this.entries.set(id, { pn: [], info: {} });
    }
    return this;
  }

  public addPartNumber(partNumber: string): void {
    for (const entry of this.entries.values()) {
      if (!entry.pn.includes(partNumber)) {
        entry.pn.push(partNumber);
      }
    }
  }

  public toJSON(): Record<string, IdDbEntry> {
    return Object.fromEntries(this.entries);
  }
}
