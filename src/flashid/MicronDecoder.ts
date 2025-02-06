import { FlashIdDecoder } from './FlashIdDecoder.js';
import { FlashIdInfo } from '../types/FlashIdInfo.js';
import { Constants } from '../types/Constants.js';
import { IntelDecoder } from './IntelDecoder.js';
import { IdDefinition } from '../types/IdDefinition.js';

export class MicronDecoder extends FlashIdDecoder {
  private static readonly ID_DEFINITION: IdDefinition = {
    "2": {
      ...IntelDecoder.ID_DEFINITION["2"],
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
      ...IntelDecoder.ID_DEFINITION["3"],
      "ext:enterprise": {
        dq: [7],
        def: {
          0: "false",
          1: "true"
        }
      }
    }
  };

  constructor() {
    super(Constants.VENDOR_MICRON, 0x2C, MicronDecoder.ID_DEFINITION);
  }

  public decode(id: number): FlashIdInfo {
    const info = super.decode(id);
    if (FlashIdDecoder.getByte(id, 2) === 0xDE) {
      return info.setDensity(Constants.DENSITY_GBITS.multiply(64));
    }
    return info;
  }
}
