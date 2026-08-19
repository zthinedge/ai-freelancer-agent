import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'

import { PlusIcon, SearchIcon, SparklesIcon } from './Icons'

type AppShellProps = Readonly<{
  children: ReactNode
  searchValue: string
  apiStatus: 'checking' | 'connected' | 'offline'
  onSearchChange: (value: string) => void
  onCreateProject: () => void
}>

export function AppShell({
  children,
  searchValue,
  apiStatus,
  onSearchChange,
  onCreateProject,
}: AppShellProps) {
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const focusSearch = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase() === 'k') {
        event.preventDefault()
        searchRef.current?.focus()
      }
    }
    window.addEventListener('keydown', focusSearch)
    return () => window.removeEventListener('keydown', focusSearch)
  }, [])

  return (
    <div className="app-shell">
      <header className="app-header">
        <a className="brand" href="#top" aria-label="接单智策首页">
          <span className="brand-mark" aria-hidden="true">
            <SparklesIcon />
          </span>
          <span className="brand-copy">
            <strong>接单智策</strong>
            <small>Freelancer Agent</small>
          </span>
        </a>

        <label className="global-search">
          <SearchIcon />
          <span className="sr-only">搜索项目</span>
          <input
            ref={searchRef}
            type="search"
            aria-keyshortcuts="Control+K Meta+K"
            value={searchValue}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="搜索项目、服务或客户需求"
          />
          <kbd>⌘ K</kbd>
        </label>

        <div className="header-actions">
          <span className={`live-status ${apiStatus}`} role="status">
            <i aria-hidden="true" />
            {apiStatus === 'connected'
              ? 'API 已连接'
              : apiStatus === 'offline'
                ? 'API 未连接'
                : 'API 检查中'}
          </span>
          <button className="header-create" type="button" onClick={onCreateProject}>
            <PlusIcon />
            <span>新建分析</span>
          </button>
        </div>
      </header>
      <main>{children}</main>
      <nav className="mobile-nav" aria-label="移动端主导航">
        <a href="#top">首页</a>
        <button type="button" onClick={onCreateProject}>
          <PlusIcon />
          新建
        </button>
        <a href="#project-board">项目</a>
      </nav>
    </div>
  )
}
