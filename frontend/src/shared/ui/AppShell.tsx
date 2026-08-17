import type { ReactNode } from 'react'


type AppShellProps = Readonly<{
  children: ReactNode
}>


export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">接</span>
          <span>
            <strong>接单智策</strong>
            <small>AI Freelancer Agent</small>
          </span>
        </div>
        <span className="status">P1 · Architecture Ready</span>
      </header>
      <main>{children}</main>
    </div>
  )
}
