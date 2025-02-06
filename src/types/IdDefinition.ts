import { DensityUnit } from './Constants.js';

export interface IdRule {
  dq: number[];
  def: Record<number, string | number | DensityUnit>;
}

export interface IdRules {
  [name: string]: IdRule;
}

export interface IdDefinition {
  [key: string]: IdRules;
}
