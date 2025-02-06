import type { FlashInfo } from '../types/FlashInfo.js';
import type { FlashInterface } from '../types/FlashInterface.js';
import type { Classification } from '../types/Classification.js';

export class FlashInfoImpl implements FlashInfo {
  public partNumber: string = '';
  public vendor: string = '';
  public type: string = '';
  public density: string = '';
  public deviceWidth: number = 0;
  public cellLevel: string = '';
  public processNode: string = '';
  public generation: string = '';
  public interface: FlashInterface = {
    toggle: false,
    async: false,
    sync: false
  };
  public classification: Classification = {
    ce: -1,
    ch: -1,
    die: -1,
    rb: -1
  };
  public voltage: string = '';
  public package: string = '';
  public controller: string[] = [];
  public remark: string = '';
  public extraInfo: Record<string, string> = {};
  public flashId: string[] = [];
  public productionDate?: string;

  public setPartNumber(partNumber: string): this {
    this.partNumber = partNumber;
    return this;
  }

  public setVendor(vendor: string): this {
    this.vendor = vendor;
    return this;
  }

  public setType(type: string): this {
    this.type = type;
    return this;
  }

  public setDensity(density: string): this {
    this.density = density;
    return this;
  }

  public setDeviceWidth(deviceWidth: number): this {
    this.deviceWidth = deviceWidth;
    return this;
  }

  public setCellLevel(cellLevel: string): this {
    this.cellLevel = cellLevel;
    return this;
  }

  public setProcessNode(processNode: string): this {
    this.processNode = processNode;
    return this;
  }

  public setGeneration(generation: string): this {
    this.generation = generation;
    return this;
  }

  public setInterface(iface: FlashInterface): this {
    this.interface = iface;
    return this;
  }

  public setClassification(classification: Classification): this {
    this.classification = classification;
    return this;
  }

  public setVoltage(voltage: string): this {
    this.voltage = voltage;
    return this;
  }

  public setPackage(pkg: string): this {
    this.package = pkg;
    return this;
  }

  public setController(controller: string[]): this {
    this.controller = controller;
    return this;
  }

  public setRemark(remark: string): this {
    this.remark = remark;
    return this;
  }

  public setExt(ext: Record<string, string>): this {
    this.extraInfo = ext;
    return this;
  }

  public setFlashId(flashId: string[]): this {
    this.flashId = flashId;
    return this;
  }

  public setProductionDate(date: string): this {
    this.productionDate = date;
    return this;
  }
}
