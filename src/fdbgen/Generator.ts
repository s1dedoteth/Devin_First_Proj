import { Fdb } from '../database/Fdb.js';

export abstract class Generator {
  public static getDirName(): string {
    throw new Error("Method not implemented");
  }

  public static merge(fdb: Fdb, content: string, filename: string): void {
    throw new Error("Method not implemented");
  }
}
