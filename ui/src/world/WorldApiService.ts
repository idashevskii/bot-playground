import { injectable, inject } from 'inversify';
import { ApiService } from '@/core/ApiService';
import type {
  ExtendedWorldDto,
  StageDto,
  StepDto,
  WorldActionDefDto,
  WorldActionDto,
  WorldCreateDto,
  WorldDto,
  WorldStatusDto,
  WorldUpdateDto,
} from './world-dto';
import { ApiDrivenFormService, type ApiDriver } from '@/core/ApiDrivenFormService';
import { useWs } from '@/utils/ws';

@injectable()
export class WorldApiService {
  public constructor(
    @inject(ApiService) private apiService: ApiService,
    @inject(ApiDrivenFormService) private apiDrivenFormService: ApiDrivenFormService,
  ) {}

  public async getWorlds(): Promise<WorldDto[]> {
    return this.apiService.fetch({ method: 'GET', endpoint: 'worlds' });
  }

  public async getWorldsExtended(): Promise<ExtendedWorldDto[]> {
    return this.apiService.fetch({ method: 'GET', endpoint: 'worlds/extended' });
  }

  public async getWorld(id: number): Promise<WorldDto> {
    return this.apiService.fetch({ method: 'GET', endpoint: `worlds/${id}` });
  }

  public async deleteWorld(wold: WorldDto): Promise<WorldDto[]> {
    return this.apiService.fetch({ method: 'DELETE', endpoint: `worlds/${wold.id}` });
  }

  public async clearWorld(wold: WorldDto): Promise<WorldDto[]> {
    return this.apiService.fetch({ method: 'POST', endpoint: `worlds/${wold.id}/clear` });
  }

  public makeCreateWorldDriver(): ApiDriver<WorldCreateDto> {
    return this.apiDrivenFormService.createFormDriver({ method: 'POST', endpoint: 'worlds' });
  }

  public makeEditWorldDriver(): ApiDriver<WorldUpdateDto, WorldDto> {
    return this.apiDrivenFormService.createFormDriver({
      method: 'PATCH',
      endpoint: 'worlds/{entityId}',
      pathParams: (entity) => ({ entityId: entity.id }),
    });
  }

  public async getWorldStages(id: number): Promise<StageDto[]> {
    return this.apiService.fetch({ method: 'GET', endpoint: `worlds/${id}/stages` });
  }

  public async getWorldStatus(id: number): Promise<WorldStatusDto> {
    return this.apiService.fetch({ method: 'GET', endpoint: `worlds/${id}/status` });
  }

  public async getWorldActions(id: number): Promise<WorldActionDefDto[]> {
    return this.apiService.fetch({ method: 'GET', endpoint: `worlds/${id}/actions/schema` });
  }

  public async sendAction(id: number, data: WorldActionDto) {
    return this.apiService.fetch({ method: 'POST', endpoint: `worlds/${id}/actions/add`, data });
  }

  public async worldStop(id: number): Promise<void> {
    return this.apiService.fetch({ method: 'POST', endpoint: `worlds/${id}/stop` });
  }

  public async worldStart(id: number, maxSteps?: number): Promise<void> {
    return this.apiService.fetch({
      method: 'POST',
      endpoint: `worlds/${id}/start`,
      query: maxSteps ? { maxSteps } : undefined,
    });
  }

  public async getStep(id: number): Promise<StepDto> {
    return this.apiService.fetch({ method: 'GET', endpoint: `steps/${id}` });
  }

  public async describeStep(id: number): Promise<Record<string, string>> {
    return this.apiService.fetch({ method: 'GET', endpoint: `steps/${id}/describe` });
  }

  public useWatchStatusWs(id: number) {
    return useWs(this.apiService.makeUrl(`worlds/ws/${id}/watch-status`));
  }

  public createStepPreviewUrl(id: number) {
    return this.apiService.makeUrl(`steps/${id}/render`);
  }
}
