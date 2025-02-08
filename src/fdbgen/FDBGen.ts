import { Generator } from './Generator.js';
import { Logger } from '../utils/Logger.js';
import { Fdb } from '../database/Fdb.js';
import { Extra } from './generators/Extra.js';
import { SiliconMotionForceFlash } from './generators/SiliconMotionForceFlash.js';
import { SiliconMotionUFD } from './generators/SiliconMotionUFD.js';
import { SiliconMotionSSD } from './generators/SiliconMotionSSD.js';
import { JMicron } from './generators/JMicron.js';
import { Maxiotek } from './generators/Maxiotek.js';
import { Maxio } from './generators/Maxio.js';
import { SandForce } from './generators/SandForce.js';
import { AlcorMicro } from './generators/AlcorMicro.js';
import { ChipsBank } from './generators/ChipsBank.js';
import { Innostor } from './generators/Innostor.js';
import { PhisonSSD } from './generators/PhisonSSD.js';
import path from 'node:path';
import fs from 'node:fs';

export class FDBGen {
  private static generators: Map<string, typeof Generator> = new Map();

  public static registerGenerator(generatorClass: typeof Generator): void {
    if (generatorClass.prototype instanceof Generator) {
      this.generators.set(generatorClass.getDirName().toLowerCase(), generatorClass);
    }
  }

  public static init(): void {
    // Full Flash Database
    this.registerGenerator(SiliconMotionForceFlash);
    // Have 6Bytes FlashId
    this.registerGenerator(SiliconMotionUFD);
    this.registerGenerator(SiliconMotionSSD);
    // May not have complete FlashId
    this.registerGenerator(JMicron);
    this.registerGenerator(Maxiotek);
    this.registerGenerator(Maxio);
    // No flash id
    this.registerGenerator(SandForce);
    this.registerGenerator(AlcorMicro);
    // Unreliable Part Number
    this.registerGenerator(ChipsBank);
    this.registerGenerator(Innostor);
    this.registerGenerator(PhisonSSD);
  }

  public static generate(version: string, dbPath: string, extra = false): Record<string, unknown> {
    if (!dbPath.endsWith(path.sep)) {
      dbPath += path.sep;
    }

    const fdb = new Fdb({
      info: {
        name: "iTXTech FlashDetector Flash Database",
        website: "https://github.com/iTXTech/FlashDetector",
        version: version,
        time: new Date().toUTCString(),
        controllers: []
      },
      iddb: {}
    });

    const dirs = Array.from(this.generators.keys());
    for (const dir of dirs) {
      const dirPath = path.join(dbPath, dir);
      if (fs.existsSync(dirPath)) {
        const generator = this.generators.get(dir.toLowerCase());
        const files = fs.readdirSync(dirPath);
        for (const file of files) {
          if (file !== '.' && file !== '..') {
            const filePath = path.join(dirPath, file);
            Logger.debug(`Merging ${generator?.constructor.name} => ${path.basename(filePath)}`);
            generator?.merge(fdb, fs.readFileSync(filePath, 'utf8'), file);
          }
        }
      }
    }

    if (extra) {
      Logger.debug("Merging extra.json");
      const extraPath = path.join(dbPath, "extra.json");
      if (fs.existsSync(extraPath)) {
        const content = fs.readFileSync(extraPath, 'utf8');
        Extra.merge(fdb, content, "extra.json");
      }
    }

    Logger.debug("Add Part Numbers to IDDB");
    const iddb = fdb.getIddb();
    for (const vendor of fdb.getVendors()) {
      const partNumbers = vendor.getPartNumbers();
      for (const [partNumber, info] of Object.entries(partNumbers)) {
        if (!info) {
          Logger.error(`Invalid vendor info for ${partNumber}: info is null or undefined`);
          continue;
        }
        const flashIds = info.id;
        if (!Array.isArray(flashIds) || !flashIds.length) {
          Logger.error(`Invalid vendor info for ${partNumber}: missing or invalid id array`);
          continue;
        }
        for (const id of flashIds) {
          iddb.getFlashId(id, true).addPartNumber(`${vendor.getName()} ${partNumber}`);
        }
      }
    }

    Logger.debug("FDB has been generated.");

    return fdb.toJSON();
  }
}
