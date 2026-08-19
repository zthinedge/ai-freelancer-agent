import type { ServiceType } from './project'

export type ServicePresentation = Readonly<{
  value: ServiceType
  label: string
  shortLabel: string
  symbol: string
  tone: string
}>

export const SERVICE_PRESENTATIONS: ReadonlyArray<ServicePresentation> = [
  { value: 'auto_detect', label: '自动识别', shortLabel: '全部', symbol: '✦', tone: 'violet' },
  { value: 'website', label: '网站开发', shortLabel: '网站', symbol: '⌘', tone: 'blue' },
  { value: 'ai_application', label: 'AI 应用', shortLabel: 'AI', symbol: '◎', tone: 'violet' },
  { value: 'ecommerce', label: '电商 / 小程序', shortLabel: '电商', symbol: '◇', tone: 'orange' },
  { value: 'presentation', label: '演示文稿', shortLabel: 'PPT', symbol: '▣', tone: 'pink' },
  { value: 'content', label: '内容创作', shortLabel: '内容', symbol: '✎', tone: 'yellow' },
  { value: 'design', label: '视觉设计', shortLabel: '设计', symbol: '◐', tone: 'coral' },
  { value: 'data_analysis', label: '数据分析', shortLabel: '数据', symbol: '⌁', tone: 'green' },
  { value: 'video', label: '视频制作', shortLabel: '视频', symbol: '▶', tone: 'red' },
  { value: 'other', label: '其他服务', shortLabel: '其他', symbol: '＋', tone: 'slate' },
]

export function getServicePresentation(serviceType: ServiceType): ServicePresentation {
  const fallback: ServicePresentation = {
    value: 'other',
    label: '其他服务',
    shortLabel: '其他',
    symbol: '·',
    tone: 'slate',
  }

  return SERVICE_PRESENTATIONS.find((item) => item.value === serviceType) ?? fallback
}
