import { PartNumberInfo } from '../types/Database.js';

export class PartNumberInfoImpl implements PartNumberInfo {
  private _pn: string;
  private _id: string[] = [];
  private _l?: string;
  private _c?: string;
  private _v?: string;
  private _i?: {
    async: boolean;
    sync: boolean;
    toggle: boolean;
  };
  private _t: string[] = [];
  private _m?: string;
  private _d?: number;
  private _e?: number;
  private _r?: number;
  private _n?: number;
  private _p?: number;
  private _ps?: number;
  private _bs?: number;
  private _ts?: number;
  private _ext?: Record<string, unknown>;

  constructor(pn: string, arr: any = null) {
    this._pn = pn.toUpperCase();
    if (arr) {
      this._id = arr.id ?? [];
      this._l = arr.l;
      this._c = arr.c;
      this._v = arr.v;
      this._i = arr.i;
      this._t = arr.t ?? [];
      this._m = arr.m;
      this._d = arr.d;
      this._e = arr.e;
      this._r = arr.r;
      this._n = arr.n;
      this._p = arr.p;
      this._ps = arr.ps;
      this._bs = arr.bs;
      this._ts = arr.ts;
      this._ext = arr.ext;
    }
  }

  public getPartNumber(): string {
    return this._pn;
  }

  public getFlashIds(): string[] {
    return this._id;
  }

  public getProcessNode(): string {
    return this._l ?? '';
  }

  public getCellLevel(): string {
    return this._c ?? '';
  }

  public getControllers(): string[] {
    return this._t;
  }

  public getRemark(): string {
    return this._m ?? '';
  }

  public getDie(): number {
    return this._d ?? -1;
  }

  public getCe(): number {
    return this._e ?? -1;
  }

  public getRb(): number {
    return this._r ?? -1;
  }

  public getCh(): number {
    return this._n ?? -1;
  }

  public toJSON(): any {
    const json: any = {};
    if (this._id.length > 0) json.id = this._id;
    if (this._l) json.l = this._l;
    if (this._c) json.c = this._c;
    if (this._v) json.v = this._v;
    if (this._i) json.i = this._i;
    if (this._t.length > 0) json.t = this._t;
    if (this._m) json.m = this._m;
    if (this._d !== undefined) json.d = this._d;
    if (this._e !== undefined) json.e = this._e;
    if (this._r !== undefined) json.r = this._r;
    if (this._n !== undefined) json.n = this._n;
    if (this._p !== undefined) json.p = this._p;
    if (this._ps !== undefined) json.ps = this._ps;
    if (this._bs !== undefined) json.bs = this._bs;
    if (this._ts !== undefined) json.ts = this._ts;
    if (this._ext) json.ext = this._ext;
    return json;
  }
}
