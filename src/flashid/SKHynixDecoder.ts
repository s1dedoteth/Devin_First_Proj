import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { Constants } from '../types/Constants.js';
import { IdDefinition } from '../types/IdDefinition.js';

export class SKHynixDecoder extends FlashIdDecoder {
  private static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      density: {
        dq: [7, 6, 5, 4, 3, 2, 1, 0],
        def: {
          211: Constants.DENSITY_GBITS.multiply(8),
          213: Constants.DENSITY_GBITS.multiply(16),
          215: Constants.DENSITY_GBITS.multiply(32),
          222: Constants.DENSITY_GBITS.multiply(64),
          58: Constants.DENSITY_GBITS.multiply(128),
          90: Constants.DENSITY_GBITS.multiply(256),
          122: Constants.DENSITY_GBITS.multiply(512),
          137: Constants.DENSITY_TBITS.multiply(1)
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
      "ext:simultaneouslyProgrammedPages": {
        dq: [5, 4],
        def: {
          0: "1",
          1: "2",
          2: "4",
          3: "8"
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
          0: 2,
          1: 4,
          2: 8,
          3: 16
        }
      },
      blockSize: {
        dq: [7, 5, 4],
        def: {
          0: "2KB",
          1: "4KB",
          2: "8KB",
          3: "16KB",
          4: "32KB",
          5: "16B"
        }
      }
    },
    "5": {
      plane: {
        dq: [3, 2],
        def: {
          0: 1,
          1: 2,
          2: 4,
          3: 8
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
          0: "Legacy",
          1: "Toggle"
        }
      }
    }
  };

  constructor() {
    super(Constants.VENDOR_SKHYNIX, 0xAD, SKHynixDecoder.ID_DEFINITION);
  }

  public decode(id: number): FlashIdInfo {
    const info = super.decode(id);
    if (FlashIdDecoder.getByte(id, 2) === 0xDE) {
      return info.setDensity(Constants.DENSITY_GBITS.multiply(64));
    }
    return info;
  }
}
