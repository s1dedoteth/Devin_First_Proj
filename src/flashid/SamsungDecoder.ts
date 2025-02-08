import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { Constants } from '../types/Constants.js';
import { IdDefinition } from '../types/IdDefinition.js';

export class SamsungDecoder extends FlashIdDecoder {
  protected static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      density: {
        dq: [4, 3, 2, 1, 0],
        def: {
          0b10011: Constants.DENSITY_GBITS.multiply(8),
          0b10101: Constants.DENSITY_GBITS.multiply(16),
          0b10111: Constants.DENSITY_GBITS.multiply(32),
          0b11010: Constants.DENSITY_GBITS.multiply(128),
          0b11100: Constants.DENSITY_GBITS.multiply(256),
          0b11110: Constants.DENSITY_GBITS.multiply(512),
          0b11111: Constants.DENSITY_TBITS.multiply(1)
        }
      }
    },
    "3": {
      die: {
        dq: [1, 0],
        def: {
          0b00: 1,
          0b01: 2,
          0b10: 4,
          0b11: 8
        }
      },
      cellLevel: {
        dq: [3, 2],
        def: {
          0b00: 1,
          0b01: 2,
          0b10: 3,
          0b11: 4
        }
      },
      "ext:simultaneouslyProgrammedPages": {
        dq: [5, 4],
        def: {
          0b00: "1",
          0b01: "2",
          0b10: "4",
          0b11: "8"
        }
      },
      "ext:interleave": {
        dq: [6],
        def: {
          0: "false",
          1: "true"
        }
      },
      "ext:cache": {
        dq: [7],
        def: {
          0: "false",
          1: "true"
        }
      }
    },
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
          0b011: 1024
        }
      },
      "ext:redundantAreaSize": {
        dq: [6, 3, 2],
        def: {
          0b001: "128B",
          0b010: "218B",
          0b011: "400B",
          0b100: "436B"
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
          0b000: "1bit/512B",
          0b001: "2bit/512B",
          0b010: "4bit/512B",
          0b011: "8bit/512B",
          0b100: "16bit/512B",
          0b101: "24bit/1KB"
        }
      }
    },
    "6": {
      processNode: {
        dq: [3, 2, 1, 0],
        def: {
          0x0: "50nm",
          0x1: "40nm",
          0x2: "30nm",
          0x3: "27nm",
          0x4: "21nm",
          0x5: "19nm",
          0x6: "16nm",
          0x7: "24L 3DV1",
          0x8: "32L 3DV2",
          0x9: "48L 3DV3",
          0xA: "14nm",
          0xB: "64L 3DV4",
          0xC: "92L 3DV5",
          0xD: "128L 3DV6"
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
          0: "Conventional",
          1: "ToggleDDR"
        }
      }
    }
  };

  constructor() {
    super(Constants.VENDOR_SAMSUNG, 0xEC, SamsungDecoder.ID_DEFINITION);
  }

  public decode(id: number): FlashIdInfo {
    const info = super.decode(id);
    if (FlashIdDecoder.getByte(id, 2) === 0xDE) {
      return info.setDensity(Constants.DENSITY_GBITS.multiply(64));
    }
    return info;
  }
}
