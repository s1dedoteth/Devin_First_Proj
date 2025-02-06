import { Generator } from '../Generator.js';
import { Fdb } from '../../database/Fdb.js';

export class Extra extends Generator {
  public static getDirName(): string {
    return "Extra";
  }

  public static merge(fdb: Fdb, content: string, filename: string): void {
    const data = JSON.parse(content);
    fdb.mergeFlashData(data);
  }
}
