import type { FlashInfo } from './FlashInfo.js';

export interface Decoder {
  getName(): string;
  check(partNumber: string): boolean;
  decode(partNumber: string): FlashInfo;
  getFlashInfoFromFdb(info: FlashInfo): FlashInfo | null;
}
