import type { FlashIdInfo } from './FlashIdInfo.js';

export interface FlashIdInfoExtended extends FlashIdInfo {
  id: string;
  die: number;
  plane: number;
  pageSize: number;
  blockSize: number;
  controllers: string[];
  partNumbers: string[];

  setId(id: string): this;
  setDie(die: string): this;
  setPlane(plane: string): this;
  setPageSize(pageSize: string): this;
  setBlockSize(blockSize: string | null): this;
  setControllers(controllers: string[]): this;
  setPartNumbers(partNumbers: string[]): this;
}
