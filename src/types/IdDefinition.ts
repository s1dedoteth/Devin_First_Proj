export interface IdDefinition {
  id: string;
  vendor: string;
  cellLevel: string;
  density: string;
  processNode: string;
  voltage: string;
  ext: Record<string, string>;
}
