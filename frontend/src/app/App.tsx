import { useState } from 'react'

import { WorkspacePage } from '../pages/workspace/WorkspacePage'
import type { AiRuntimeStatus } from '../shared/api/systemStatus'
import { AppShell } from '../shared/ui/AppShell'

export function App() {
  const [searchValue, setSearchValue] = useState('')
  const [focusSignal, setFocusSignal] = useState(0)
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'offline'>('checking')
  const [aiRuntime, setAiRuntime] = useState<AiRuntimeStatus | null>(null)

  return (
    <AppShell
      searchValue={searchValue}
      apiStatus={apiStatus}
      aiRuntime={aiRuntime}
      onSearchChange={setSearchValue}
      onCreateProject={() => setFocusSignal((value) => value + 1)}
    >
      <WorkspacePage
        searchValue={searchValue}
        focusSignal={focusSignal}
        onApiStatusChange={setApiStatus}
        onAiRuntimeChange={setAiRuntime}
      />
    </AppShell>
  )
}
