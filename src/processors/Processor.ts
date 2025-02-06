import type { FlashInfo } from '../types/FlashInfo.js';

export interface Processor {
  getName(): string;
  process(info: FlashInfo): FlashInfo;
}
