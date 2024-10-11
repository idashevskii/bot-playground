export interface WorldBaseDto {
  title: string;
}

export interface WorldCreateDto extends WorldBaseDto {
  plugin: string;
}

export interface WorldUpdateDto extends WorldBaseDto {
  config: string;
}

export interface WorldDto extends WorldBaseDto {
  id: number;
  plugin: string;
  config?: string;
}

export interface ExtendedWorldDto extends WorldDto {
  initialized: boolean;
  running: boolean;
}

export interface StageDto {
  id: number;
  title: string;
  worldId: number;
}

export interface WorldStatusStepDto {
  id: number;
  stageId: number;
}

export interface WorldStatusDto {
  isRunning: boolean;
  steps: WorldStatusStepDto[];
}

export interface WorldActionDefDto {
  name: string;
  title: string;
  shortcut?: string;
}

export interface WorldActionDto {
  name: string;
}

export interface StepDto {
  stageId: number;
  state: string;
  actions: string;
  logs: string;
  interactions: string;
}
