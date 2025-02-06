export class FlashIdInfo {
  private type: string = '';
  private vendor: string = '';
  private cellLevel: string = '';
  private density: string = '';
  private processNode: string = '';
  private voltage: string = '';
  private ext: Record<string, any> = {};

  constructor(id: number) {
    // Initialize with empty values
  }

  public getType(): string {
    return this.type;
  }

  public setType(type: string): this {
    this.type = type;
    return this;
  }

  public getVendor(): string {
    return this.vendor;
  }

  public setVendor(vendor: string): this {
    this.vendor = vendor;
    return this;
  }

  public getCellLevel(): string {
    return this.cellLevel;
  }

  public setCellLevel(cellLevel: string): this {
    this.cellLevel = cellLevel;
    return this;
  }

  public getDensity(): string {
    return this.density;
  }

  public setDensity(density: string): this {
    this.density = density;
    return this;
  }

  public getProcessNode(): string {
    return this.processNode;
  }

  public setProcessNode(processNode: string): this {
    this.processNode = processNode;
    return this;
  }

  public getVoltage(): string {
    return this.voltage;
  }

  public setVoltage(voltage: string): this {
    this.voltage = voltage;
    return this;
  }

  public getExt(): Record<string, any> {
    return { ...this.ext };
  }

  public setExt(ext: Record<string, any>): this {
    this.ext = { ...ext };
    return this;
  }
}
