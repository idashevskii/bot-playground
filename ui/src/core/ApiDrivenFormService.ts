import { injectable, inject } from 'inversify';
import { ApiService } from '@/core/ApiService';
import type { JsonSchema } from '@jsonforms/core';
import { OpenApiService } from './OpenApiService';

interface SubmitResponse {}

export type PathData = Record<string, string | number>;

export interface ApiDriver<T, PD = never> {
  getSchema(): Promise<JsonSchema>;
  submitData(data: T, paramsData?: PD): Promise<SubmitResponse>;
}

@injectable()
export class ApiDrivenFormService {
  public constructor(
    @inject(OpenApiService) private openApiService: OpenApiService,
    @inject(ApiService) private apiService: ApiService,
  ) {}

  public createFormDriver<T, PD = never>({
    method,
    endpoint,
    pathParams,
  }: {
    method: string;
    endpoint: string;
    pathParams?: (data: PD) => PathData;
  }): ApiDriver<T, PD> {
    return {
      getSchema: async () => {
        return this.openApiService.getEndpointSchema(method, endpoint);
      },
      submitData: async (data: T, paramsData?: PD) => {
        let filledEndpoint = endpoint;
        if (pathParams && paramsData) {
          filledEndpoint = this.fillEndpoint(filledEndpoint, pathParams(paramsData));
        }
        await this.apiService.fetch({ method, endpoint: filledEndpoint, data });
        return {};
      },
    };
  }
  private fillEndpoint(endpoint: string, pathData: PathData) {
    for (const [key, value] of Object.entries(pathData)) {
      endpoint = endpoint.replace(`{${key}}`, String(value));
    }
    return endpoint;
  }
}
