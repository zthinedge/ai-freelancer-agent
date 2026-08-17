export type HttpRequest = Readonly<{
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  signal?: AbortSignal
}>

export interface HttpClient {
  request<Response>(request: HttpRequest): Promise<Response>
}
