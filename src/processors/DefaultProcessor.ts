import type { Processor } from './Processor.js';
import type { FlashInfo } from '../types/FlashInfo.js';

export class DefaultProcessor implements Processor {
  public getName(): string {
    return 'Default';
  }

  public process(info: FlashInfo): FlashInfo {
    return info;
  }
}
