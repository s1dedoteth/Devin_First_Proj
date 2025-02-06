export interface DensityUnit {
  value: number;
  unit: string;
  toString(): string;
  multiply(n: number): DensityUnit;
}

export class DensityValue implements DensityUnit {
  constructor(public value: number, public unit: string) {}

  toString(): string {
    return `${this.value}${this.unit}`;
  }

  multiply(n: number): DensityUnit {
    return new DensityValue(this.value * n, this.unit);
  }

  valueOf(): number {
    return this.value;
  }
}

export const Constants = {
  UNKNOWN: 'Unknown',
  UNKNOWN_PROP: -1,
  USA: 'USA',
  SINGAPORE: 'Singapore',
  ITALY: 'Italy',
  JAPAN: 'Japan',
  CHINA: 'China',
  TAIWAN: 'Taiwan',
  KOREA: 'Korea',
  MIXED: 'Mixed',
  ISRAEL: 'Israel',
  IRELAND: 'Ireland',
  MALAYSIA: 'Malaysia',
  PHILIPPINES: 'Philippines',
  VENDOR_MICRON: 'Micron',
  VENDOR_INTEL: 'Intel',
  VENDOR_SAMSUNG: 'Samsung',
  VENDOR_SKHYNIX: 'SK Hynix',
  VENDOR_KIOXIA: 'Kioxia',
  VENDOR_WDC: 'Western Digital',
  VENDOR_YANGTZE: 'YMTC',
  VENDOR_PHISON: 'Phison',
  VENDOR_SPECTEK: 'SpecTek',
  DIFFUSION: 'Diffusion',
  ENCAPSULATION: 'Encapsulation',
  MICRON_PN: 'Micron Part Number',
  DENSITY_GBITS: new DensityValue(1, 'Gb'),
  DENSITY_TBITS: new DensityValue(1024, 'Gb')
} as const;
