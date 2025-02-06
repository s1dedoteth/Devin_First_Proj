export class FlashIdInfo {
  public s: number;  // Die
  public p: number;  // Plane
  public b: number;  // Block
  public t: string[];  // Controllers
  public n: string[];  // Part Numbers
  public vendor: string;
  public cellLevel: string;
  public density: string;
  public processNode: string;
  public voltage: string;
  public ext: Record<string, string>;

  constructor(id: number) {
    this.s = -1;
    this.p = -1;
    this.b = -1;
    this.t = [];
    this.n = [];
    this.vendor = '';
    this.cellLevel = '';
    this.density = '';
    this.processNode = '';
    this.voltage = '';
    this.ext = {};
  }

  public setVendor(vendor: string): this {
    this.vendor = vendor;
    return this;
  }

  public setCellLevel(cellLevel: string): this {
    this.cellLevel = cellLevel;
    return this;
  }

  public setDensity(density: string): this {
    this.density = density;
    return this;
  }

  public setProcessNode(processNode: string): this {
    this.processNode = processNode;
    return this;
  }

  public setVoltage(voltage: string): this {
    this.voltage = voltage;
    return this;
  }

  public setExt(ext: Record<string, string>): this {
    this.ext = ext;
    return this;
  }
}
