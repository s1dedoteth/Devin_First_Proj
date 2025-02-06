import { Generator } from '../Generator.js';
import { Fdb } from '../../database/Fdb.js';

export class SiliconMotionSSD extends Generator {
  public static getDirName(): string {
    return "SMSSD";
  }

  public static merge(fdb: Fdb, content: string, filename: string): void {
    const data = JSON.parse(content);
    fdb.mergeFlashData(data);
  }
}
