export type RuntimeConfig = Readonly<{
  apiBaseUrl: string
  environment: 'development' | 'test' | 'production'
}>
