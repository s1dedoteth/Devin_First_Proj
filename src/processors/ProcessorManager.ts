import type { Processor } from './Processor.js';
import type { FlashInfo } from '../types/FlashInfo.js';

export class ProcessorManager {
  private static instance: ProcessorManager;
  private processors: Processor[] = [];

  private constructor() {}

  public static getInstance(): ProcessorManager {
    if (!ProcessorManager.instance) {
      ProcessorManager.instance = new ProcessorManager();
    }
    return ProcessorManager.instance;
  }

  public registerProcessor(processor: Processor): void {
    this.processors.push(processor);
  }

  public processFlashInfo(info: FlashInfo): FlashInfo {
    let result = info;
    for (const processor of this.processors) {
      result = processor.process(result);
    }
    return result;
  }
}
