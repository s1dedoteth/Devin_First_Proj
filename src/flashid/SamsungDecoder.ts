import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { Constants } from '../types/Constants.js';
import { IdDefinition } from '../types/IdDefinition.js';

export class SamsungDecoder extends FlashIdDecoder {
  private static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      density: {
        dq: [7, 6, 5, 4, 3],
        def: {
          19: Constants.DENSITY_GBITS.multiply(32),
          21: Constants.DENSITY_GBITS.multiply(64),
          23: Constants.DENSITY_GBITS.multiply(128),
          26: Constants.DENSITY_GBITS.multiply(256),
          28: Constants.DENSITY_GBITS.multiply(512),
          30: Constants.DENSITY_TBITS.multiply(1),
          31: Constants.DENSITY_TBITS.multiply(2)
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
        dq: [1, 0],
        def: {
          0: 2,
          1: 4,
          2: 8,
          3: 16
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
