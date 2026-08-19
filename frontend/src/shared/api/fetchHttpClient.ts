import type { ApiErrorResponse } from './contracts'
import type { HttpClient, HttpRequest } from './httpClient'

export class HttpError extends Error {
  readonly status: number
  readonly errorCode: string
  readonly traceId: string | null

  constructor(status: number, message: string, errorCode = 'http_error', traceId: string | null = null) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.errorCode = errorCode
    this.traceId = traceId
  }
}

export class FetchHttpClient implements HttpClient {
  constructor(private readonly baseUrl: string) {}

  async request<Response>({ path, method, body, signal }: HttpRequest): Promise<Response> {
    const init: RequestInit = {
      method,
      ...(signal === undefined ? {} : { signal }),
      ...(body === undefined
        ? {}
        : {
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
          }),
    }
    const response = await fetch(`${this.baseUrl}${path}`, init)

    if (!response.ok) {
      const error = await this.readError(response)
      throw new HttpError(response.status, error.message, error.error_code, error.trace_id)
    }

    return (await response.json()) as Response
  }

  private async readError(response: Response): Promise<ApiErrorResponse> {
    try {
      const payload: unknown = await response.json()
      if (
        typeof payload === 'object' &&
        payload !== null &&
        'message' in payload &&
        typeof payload.message === 'string'
      ) {
        return {
          schema_version: '1.0.0',
          error_code:
            'error_code' in payload && typeof payload.error_code === 'string'
              ? payload.error_code
              : 'http_error',
          message: payload.message,
          trace_id:
            'trace_id' in payload && typeof payload.trace_id === 'string'
              ? payload.trace_id
              : '',
        }
      }
    } catch {
      // The fallback below also handles non-JSON reverse-proxy responses.
    }

    return {
      schema_version: '1.0.0',
      error_code: 'invalid_error_response',
      message: `请求失败（HTTP ${response.status}）`,
      trace_id: '',
    }
  }
}
