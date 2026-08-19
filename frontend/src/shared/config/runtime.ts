export type RuntimeConfig = Readonly<{
  apiBaseUrl: string
  environment: 'development' | 'test' | 'production'
}>

const mode = import.meta.env.MODE

export const runtimeConfig: RuntimeConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '',
  environment: mode === 'production' || mode === 'test' ? mode : 'development',
}
