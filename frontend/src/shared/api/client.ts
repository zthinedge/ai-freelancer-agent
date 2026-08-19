import { runtimeConfig } from '../config/runtime'
import { FetchHttpClient } from './fetchHttpClient'

export const httpClient = new FetchHttpClient(runtimeConfig.apiBaseUrl)
