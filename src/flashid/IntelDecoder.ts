import { FlashIdDecoder } from './FlashIdDecoder.js';
import { Constants } from '../types/Constants.js';
import { IdDefinition } from '../types/IdDefinition.js';

export class IntelDecoder extends FlashIdDecoder {
  public static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      voltage: {
        dq: [2, 1, 0],
        def: {
          3: "Vcc: 2.5V/3.3V",
          4: "Vcc: 3.3V"
        }
      },
      density: {
        dq: [7, 6, 5, 4, 3],
        def: {
          9: Constants.DENSITY_GBITS.multiply(32),
          17: Constants.DENSITY_GBITS.multiply(64),
          16: Constants.DENSITY_GBITS.multiply(128),
          20: Constants.DENSITY_GBITS.multiply(256),
          22: Constants.DENSITY_GBITS.multiply(384),
          24: Constants.DENSITY_GBITS.multiply(512),
          26: Constants.DENSITY_TBITS.multiply(1),
          28: Constants.DENSITY_TBITS.multiply(2),
          30: Constants.DENSITY_TBITS.multiply(4),
          5: Constants.DENSITY_TBITS.multiply(8)
        }
      }
    },
    "3": {
      die: {
        dq: [1, 0],
        def: {
          0: 1,
          1: 2,
          2: 4,
          3: 8
        }
      },
      cellLevel: {
        dq: [3, 2],
        def: {
          0: 1,
          1: 2,
          2: 3,
          3: 4
        }
      },
      "ext:pagesPerBlock": {
        dq: [6, 5, 4],
        def: {
          6: "512/1024/1536",
          2: "9216"
        }
      }
    },
    "4": {
      pageSize: {
        dq: [2, 1, 0],
        def: {
          6: 4,
          7: 8,
          3: 8,
          2: 16,
          4: 16
        }
      }
    },
    "5": {
      plane: {
        dq: [1, 0],
        def: {
          0: 1,
          1: 2,
          2: 4
        }
      },
      "ext:blocksPerLun": {
        dq: [4, 3, 2],
        def: {
          0: "1024",
          1: "1025~2048",
          2: "2049~4096"
        }
      },
      "ext:timingModeAsync": {
        dq: [7, 6, 5],
        def: {
          0: "0 (100ns)",
          1: "1 (50ns)",
          2: "2 (35ns)",
          3: "3 (30ns)",
          4: "4 (25ns)",
          5: "5 (20ns)",
          6: "Default"
        }
      }
    },
    "6": {
      "ext:revision": {
        dq: [3, 2],
        def: {
          0: 1,
          1: 2,
          2: 3,
          3: 4
        }
      }
    }
  };

  constructor() {
    super(Constants.VENDOR_INTEL, 0x89, IntelDecoder.ID_DEFINITION);
  }
}
