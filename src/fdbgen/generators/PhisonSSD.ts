import { Generator } from '../Generator.js';
import { Fdb } from '../../database/Fdb.js';

export class PhisonSSD extends Generator {
  public static getDirName(): string {
    return "PhisonSSD";
  }

  public static merge(fdb: Fdb, content: string, filename: string): void {
    const data = JSON.parse(content);
    fdb.mergeFlashData(data);
  }
}
