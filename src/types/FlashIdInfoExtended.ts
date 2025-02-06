import type { FlashIdInfo } from './FlashIdInfo.js';

export interface FlashIdInfoExtended extends FlashIdInfo {
  id: string;
  die: number;
  plane: number;
  pageSize: number;
  blockSize: number;
  controllers: string[];
  partNumbers: string[];
}
