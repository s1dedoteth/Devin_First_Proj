import { DensityUnit } from './Constants.js';

export interface FlashIdInfo {
  getType(): string;
  setType(type: string): this;
  getVendor(): string;
  setVendor(vendor: string): this;
  getCellLevel(): string;
  setCellLevel(cellLevel: string): this;
  getDensity(): string;
  setDensity(density: string | DensityUnit): this;
  getProcessNode(): string;
  setProcessNode(processNode: string): this;
  getVoltage(): string;
  setVoltage(voltage: string): this;
  getExt(): Record<string, any>;
  setExt(ext: Record<string, any>): this;
  setPlane(plane: string): this;
  setDie(die: string): this;
  setPageSize(pageSize: string): this;
  setBlockSize(blockSize: string | null): this;
  setControllers(controllers: string[]): this;
  setPartNumbers(partNumbers: string[]): this;
  setId(id: string): this;
}

export class FlashIdInfoImpl implements FlashIdInfo {
  private _ext: Record<string, any> = {};
  private readonly _id: number;
  private _vendor: string = '';
  private _type: string = '';
  private _density: string = '';
  private _cellLevel: string = '';
  private _processNode: string = '';
  private _voltage: string = '';
  private _plane: string = '';
  private _die: string = '';
  private _pageSize: string = '';
  private _blockSize: string | null = null;
  private _controllers: string[] = [];
  private _partNumbers: string[] = [];

  constructor(id: number) {
    this._id = id;
  }

  public getType(): string {
    return this._type;
  }

  public setType(type: string): this {
    this._type = type;
    return this;
  }

  public getVendor(): string {
    return this._vendor;
  }

  public setVendor(vendor: string): this {
    this._vendor = vendor;
    return this;
  }

  public getCellLevel(): string {
    return this._cellLevel;
  }

  public setCellLevel(cellLevel: string): this {
    this._cellLevel = cellLevel;
    return this;
  }

  public getDensity(): string {
    return this._density;
  }

  public setDensity(density: string | DensityUnit): this {
    this._density = typeof density === 'string' ? density : density.toString();
    return this;
  }

  public getProcessNode(): string {
    return this._processNode;
  }

  public setProcessNode(processNode: string): this {
    this._processNode = processNode;
    return this;
  }

  public getVoltage(): string {
    return this._voltage;
  }

  public setVoltage(voltage: string): this {
    this._voltage = voltage;
    return this;
  }

  public getExt(): Record<string, any> {
    return { ...this._ext };
  }

  public setExt(ext: Record<string, any>): this {
    this._ext = { ...ext };
    return this;
  }

  public setPlane(plane: string): this {
    this._plane = plane;
    return this;
  }

  public setDie(die: string): this {
    this._die = die;
    return this;
  }

  public setPageSize(pageSize: string): this {
    this._pageSize = pageSize;
    return this;
  }

  public setBlockSize(blockSize: string | null): this {
    this._blockSize = blockSize;
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

  public setId(id: string): this {
    // _id is read-only, initialized in constructor
    return this;
  }
}
