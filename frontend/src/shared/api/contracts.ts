export type ApiErrorResponse = Readonly<{
  schema_version: '1.0.0'
  error_code: string
  message: string
  trace_id: string
}>
