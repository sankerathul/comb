import { useState } from 'react'
import { AgentPlan, AgentResult, AppState } from './types'
import { HoneycombGrid } from './components/HoneycombGrid'

export default function App() {
  const [appState, setAppState] = useState<AppState>('idle')
  const [goal, setGoal] = useState('')
  const [plan, setPlan] = useState<AgentPlan | null>(null)
  const [results, setResults] = useState<AgentResult[]>([])
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(submittedGoal: string) {
    setGoal(submittedGoal)
    setError(null)
    setPlan(null)
    setResults([])
    setAppState('planning')

    try {
      const res = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: submittedGoal }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail ?? 'Planning failed')
      }
      const agentPlan: AgentPlan = await res.json()
      setPlan(agentPlan)
      setAppState('planned')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setAppState('idle')
    }
  }

  async function handleRun() {
    if (!plan) return
    setResults([])
    setAppState('running')

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plan),
      })
      if (!res.ok) throw new Error('Run failed')
      const data: AgentResult[] = await res.json()
      setResults(data)
      setAppState('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setAppState('planned')
    }
  }

  function handleReset() {
    setAppState('idle')
    setGoal('')
    setPlan(null)
    setResults([])
    setError(null)
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 0,
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{ marginBottom: 8, textAlign: 'center' }}>
        <h1 style={{
          fontSize: 13,
          fontWeight: 700,
          letterSpacing: 6,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
        }}>
          COMB
        </h1>
        <p style={{ fontSize: 10, color: '#4b5563', letterSpacing: 2, marginTop: 2 }}>
          Collaborative Orchestration of Multi-agent Behavior
        </p>
      </div>

      {/* Honeycomb */}
      <HoneycombGrid
        appState={appState}
        goal={goal}
        plan={plan}
        results={results}
        onSubmit={handleSubmit}
      />

      {/* Controls below the grid */}
      <div style={{ height: 64, display: 'flex', alignItems: 'center', gap: 12 }}>
        {error && (
          <span style={{ fontSize: 12, color: 'var(--error)', maxWidth: 400, textAlign: 'center' }}>
            {error}
          </span>
        )}

        {appState === 'planned' && (
          <>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {plan!.agents.length} agents ready
            </span>
            <button onClick={handleRun} style={btnStyle('var(--worker)')}>
              Run Agents
            </button>
            <button onClick={handleReset} style={btnStyle('var(--ghost)', true)}>
              Reset
            </button>
          </>
        )}

        {appState === 'done' && (
          <button onClick={handleReset} style={btnStyle('var(--queen)')}>
            New Goal
          </button>
        )}
      </div>
    </div>
  )
}

function btnStyle(color: string, ghost = false): React.CSSProperties {
  return {
    padding: '8px 20px',
    background: ghost ? 'transparent' : color,
    border: `1px solid ${color}`,
    borderRadius: 6,
    color: '#f9fafb',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    letterSpacing: 0.5,
    transition: 'all 0.2s',
  }
}
