import { FlashInfo } from '../types/FlashInfo.js';
import { FlashInfoImpl } from '../core/FlashInfoImpl.js';
import { Constants } from '../types/Constants.js';
import { PartNumberInfo } from '../types/Database.js';

export abstract class AbstractDecoder {
  protected constructor(
    protected readonly vendor: string,
    protected readonly type: string,
    protected readonly processNode: string,
    protected readonly cellLevel: string,
    protected readonly voltage: string,
    protected readonly classification: {
      ce: number;
      ch: number;
      die: number;
      rb: number;
    }
  ) {}

  public decode(pn: string, dbInfo: PartNumberInfo): FlashInfo {
    const flashInfo = new FlashInfoImpl();
    flashInfo.setPartNumber(pn)
      .setVendor(this.vendor)
      .setType(this.type)
      .setDensity(Constants.UNKNOWN)
      .setDeviceWidth(0)
      .setCellLevel(dbInfo.c ?? '')
      .setProcessNode(dbInfo.l ?? '')
      .setVoltage(dbInfo.v ?? '')
      .setInterface({
        async: dbInfo.i?.async ?? false,
        sync: dbInfo.i?.sync ?? false,
        toggle: dbInfo.i?.toggle ?? false
      })
      .setClassification({
        ce: Number(dbInfo.e) || 0,
        ch: Number(dbInfo.n) || 0,
        die: Number(dbInfo.d) || 0,
        rb: Number(dbInfo.r) || 0
      })
      .setController(dbInfo.t ?? [])
      .setRemark(dbInfo.m ?? '')
      .setExt({})
      .setFlashId(dbInfo.id);
    return flashInfo;
  }
}
