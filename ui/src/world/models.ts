import type { WorldActionDto } from "./world-dto";

export interface WorldLogEntry {
  level: string;
  message: string;
}

export interface ParsedStep {
  logs: WorldLogEntry[];
  actions: WorldActionDto[];
}
