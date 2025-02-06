import { Generator } from '../Generator.js';
import { Fdb } from '../../database/Fdb.js';

export class SandForce extends Generator {
  public static getDirName(): string {
    return "SandForce";
  }

  public static merge(fdb: Fdb, content: string, filename: string): void {
    const data = JSON.parse(content);
    fdb.mergeFlashData(data);
  }
}
