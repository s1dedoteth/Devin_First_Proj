import type { FlashIdInfo } from '../types/FlashIdInfo.js';

export abstract class FlashIdDecoder {
  abstract decode(id: number): FlashIdInfo;
  abstract check(id: number): boolean;
}
