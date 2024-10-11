import { injectable, inject } from 'inversify';
import { ApiService } from '@/core/ApiService';
import type { JsonSchema } from '@jsonforms/core';
import { trimSubstrStart } from '@/utils/strings';
import type { OpenAPIV3_1 } from 'openapi-types';

interface SubmitResponse {}

@injectable()
export class OpenApiService {
  private fullSchema?: OpenAPIV3_1.Document;
  public constructor(@inject(ApiService) private apiService: ApiService) {}

  public async getEndpointSchema(method: string, endpoint: string): Promise<JsonSchema> {
    if (!this.fullSchema) {
      this.fullSchema = await this.apiService.fetch({
        method: 'GET',
        endpoint: 'openapi.json',
      });
    }
    const paths = this.fullSchema.paths;
    if (!paths) {
      throw new Error('Missing paths in OpenApi');
    }
    const path = paths[this.normalizeOpenApiPath(endpoint)];
    if (!path) {
      throw new Error(`Missing endpoint ${endpoint} in OpenApi`);
    }
    const endpoints = path[this.normalizeOpenApiMethod(method)];
    if (!endpoints || !endpoints.requestBody) {
      throw new Error(`Missing method ${method} for endpoint ${endpoint} in OpenApi`);
    }
    if (!('content' in endpoints.requestBody)) {
      throw new Error(`Missing content for ${method} for endpoint ${endpoint} in OpenApi`);
    }
    const boxedSchema = endpoints.requestBody.content['application/json'].schema;
    return {
      ...({ components: this.fullSchema.components } as any),
      ...boxedSchema,
    };
  }

  private normalizeOpenApiMethod(method: string): OpenAPIV3_1.HttpMethods {
    return method.toLowerCase() as OpenAPIV3_1.HttpMethods;
  }

  private normalizeOpenApiPath(endpoint: string) {
    return `/${trimSubstrStart(endpoint, '/')}`;
  }
}
