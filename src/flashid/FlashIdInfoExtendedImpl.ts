import { FlashIdInfo } from './FlashIdInfo.js';
import type { FlashIdInfoExtended } from '../types/FlashIdInfoExtended.js';

export class FlashIdInfoExtendedImpl extends FlashIdInfo implements FlashIdInfoExtended {
  protected _die: number = 0;
  protected _plane: number = 0;
  protected _pageSize: number = 0;
  protected _blockSize: number = 0;
  protected _controllers: string[] = [];
  protected _partNumbers: string[] = [];

  constructor(id: number) {
    super(id);
  }

  public get die(): number { return this._die; }
  public get plane(): number { return this._plane; }
  public get pageSize(): number { return this._pageSize; }
  public get blockSize(): number { return this._blockSize; }
  public get controllers(): string[] { return this._controllers; }
  public get partNumbers(): string[] { return this._partNumbers; }

  public setDie(die: string | number): this {
    this._die = typeof die === 'string' ? parseInt(die, 10) || 0 : die;
    return this;
  }

  public setPlane(plane: string | number): this {
    this._plane = typeof plane === 'string' ? parseInt(plane, 10) || 0 : plane;
    return this;
  }

  public setPageSize(pageSize: string | number): this {
    this._pageSize = typeof pageSize === 'string' ? parseInt(pageSize, 10) || 0 : pageSize;
    return this;
  }

  public setBlockSize(blockSize: string | number | null): this {
    this._blockSize = typeof blockSize === 'string' ? parseInt(blockSize, 10) || 0 : blockSize || 0;
    return this;
  }

  public setControllers(controllers: string[]): this {
    this._controllers = controllers;
    return this;
  }

  public setPartNumbers(partNumbers: string[]): this {
    this._partNumbers = partNumbers;
    return this;
  }
}
