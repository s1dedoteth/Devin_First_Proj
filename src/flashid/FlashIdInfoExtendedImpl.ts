import { FlashIdInfo } from './FlashIdInfo.js';
import type { FlashIdInfoExtended } from '../types/FlashIdInfoExtended.js';

export class FlashIdInfoExtendedImpl extends FlashIdInfo implements FlashIdInfoExtended {
  public id: string = '';
  public die: number = -1;
  public plane: number = -1;
  public pageSize: number = -1;
  public blockSize: number = -1;
  public controllers: string[] = [];
  public partNumbers: string[] = [];

  constructor(id: number) {
    super(id);
  }

  public setId(id: string): this {
    this.id = id;
    return this;
  }

  public setDie(die: number): this {
    this.die = die;
    return this;
  }

  public setPlane(plane: number): this {
    this.plane = plane;
    return this;
  }

  public setPageSize(pageSize: number): this {
    this.pageSize = pageSize;
    return this;
  }

  public setBlockSize(blockSize: number): this {
    this.blockSize = blockSize;
    return this;
  }

  public setControllers(controllers: string[]): this {
    this.controllers = controllers;
    return this;
  }

  public setPartNumbers(partNumbers: string[]): this {
    this.partNumbers = partNumbers;
    return this;
  }
}
