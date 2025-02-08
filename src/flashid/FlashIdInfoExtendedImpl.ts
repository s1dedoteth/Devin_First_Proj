import { FlashIdInfo } from './FlashIdInfo.js';
import type { FlashIdInfoExtended } from '../types/FlashIdInfoExtended.js';

export class FlashIdInfoExtendedImpl extends FlashIdInfo implements FlashIdInfoExtended {
  private _id: string = '';
  private _die: number = 0;
  private _plane: number = 0;
  private _pageSize: number = 0;
  private _blockSize: number = 0;
  private _controllers: string[] = [];
  private _partNumbers: string[] = [];

  constructor(id: number) {
    super(id);
  }

  public get id(): string { return this._id; }
  public get die(): number { return this._die; }
  public get plane(): number { return this._plane; }
  public get pageSize(): number { return this._pageSize; }
  public get blockSize(): number { return this._blockSize; }
  public get controllers(): string[] { return this._controllers; }
  public get partNumbers(): string[] { return this._partNumbers; }

  public setId(id: string): this {
    this._id = id;
    return this;
  }

  public setDie(die: string): this {
    this._die = parseInt(die, 10) || 0;
    return this;
  }

  public setPlane(plane: string): this {
    this._plane = parseInt(plane, 10) || 0;
    return this;
  }

  public setPageSize(pageSize: string): this {
    this._pageSize = parseInt(pageSize, 10) || 0;
    return this;
  }

  public setBlockSize(blockSize: string | null): this {
    this._blockSize = blockSize ? parseInt(blockSize, 10) : 0;
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
