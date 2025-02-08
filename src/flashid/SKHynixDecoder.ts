import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { Constants } from '../types/Constants.js';
import { IdDefinition } from '../types/IdDefinition.js';
import { SamsungDecoder } from './SamsungDecoder.js';

export class SKHynixDecoder extends FlashIdDecoder {
  protected static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      density: {
        dq: [7, 6, 5, 4, 3, 2, 1, 0],
        def: {
          0xD3: Constants.DENSITY_GBITS.multiply(8),
          0xD5: Constants.DENSITY_GBITS.multiply(16),
          0xD7: Constants.DENSITY_GBITS.multiply(32),
          0xDE: Constants.DENSITY_GBITS.multiply(64),
          0x3A: Constants.DENSITY_GBITS.multiply(128),
          0x5A: Constants.DENSITY_GBITS.multiply(128),
          0x3C: Constants.DENSITY_GBITS.multiply(256),
          0x5C: Constants.DENSITY_GBITS.multiply(256),
          0x3E: Constants.DENSITY_GBITS.multiply(512),
          0x5E: Constants.DENSITY_GBITS.multiply(512),
          0x89: Constants.DENSITY_TBITS.multiply(1)
        }
      }
    },
    "3": SamsungDecoder.ID_DEFINITION[3],
    "4": {
      pageSize: {
        dq: [1, 0],
        def: {
          0b00: 2,
          0b01: 4,
          0b10: 8,
          0b11: 16
        }
      },
      blockSize: {
        dq: [7, 5, 4],
        def: {
          0b000: 128,
          0b001: 256,
          0b010: 512,
          0b011: 768,
          0b100: 1024,
          0b101: 2048
        }
      },
      "ext:redundantAreaSize": {
        dq: [6, 3, 2],
        def: {
          0b110: "640B",
          0b010: "448B",
          0b001: "224B",
          0b000: "128B",
          0b011: "64B",
          0b100: "32B",
          0b101: "16B"
        }
      }
    },
    "5": {
      plane: {
        dq: [3, 2],
        def: {
          0b00: 1,
          0b01: 2,
          0b10: 4,
          0b11: 8
        }
      },
      "ext:eccLevel": {
        dq: [6, 5, 4],
        def: {
          0b000: "None",
          0b001: "1bit/512B",
          0b010: "2bit/512B",
          0b011: "4bit/512B",
          0b100: "8bit/512B",
          0b101: "24bit/512B",
          0b110: "32bit/1KB",
          0b111: "40bit/1KB"
        }
      }
    },
    "6": {
      processNode: {
        dq: [3, 2, 1, 0],
        def: {
          0x0: "48nm",
          0x1: "41nm",
          0x2: "32nm",
          0x3: "26nm",
          0x4: "20nm",
          0x5: "16nm",
          0x9: "16nm",
          0xA: "16nm"
        }
      },
      "ext:edo": {
        dq: [6],
        def: {
          0: "false",
          1: "true"
        }
      },
      "ext:interface": {
        dq: [7],
        def: {
          0: "Async Only",
          1: "Async and Sync"
        }
      }
    }
  };

  protected static readonly NEW_ID_DEFINITION: IdDefinition = {
    "6": {
      processNode: {
        dq: [7, 6, 5, 4],
        def: {
          0x5: "14nm",
          0x7: "36L 3DV2",
          0x8: "48L 3DV3",
          0x9: "72L 3DV4",
          0xA: "96L 3DV5",
          0xB: "128L 3DV6"
        }
      }
    }
  };

  constructor() {
    super(Constants.VENDOR_SKHYNIX, 0xAD, SKHynixDecoder.ID_DEFINITION);
  }

  public decode(id: number): FlashIdInfo {
    const info = super.decode(id);
    const spp = info.ext["simultaneouslyProgrammedPages"];
    if (spp) {
      info.setPlane(spp);
    }
    if (FlashIdDecoder.getByte(id, 2) === 0xDE) {
      info.setDensity(Constants.DENSITY_GBITS.multiply(64));
    }
    if (FlashIdDecoder.getByte(id, 6) >= 0x50) {
      info.setExt({}).setBlockSize(null);
      this.decodeIdDef(id, SKHynixDecoder.NEW_ID_DEFINITION, info);
    }
    return info;
  }
}
