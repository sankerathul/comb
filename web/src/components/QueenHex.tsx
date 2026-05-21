import { useState } from 'react'
import { AppState } from '../types'

interface Props {
  appState: AppState
  goal: string
  onSubmit: (goal: string) => void
}

const HEX_CLIP = 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'

export function QueenHex({ appState, goal, onSubmit }: Props) {
  const [draft, setDraft] = useState('')

  const handleSubmit = () => {
    const trimmed = draft.trim()
    if (trimmed) onSubmit(trimmed)
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div
      style={{
        width: 220,
        height: 254,
        clipPath: HEX_CLIP,
        background: 'rgba(124,58,237,0.18)',
        boxShadow: '0 0 32px 8px var(--queen-glow)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '36px 20px',
        position: 'relative',
        zIndex: 10,
      }}
    >
      {appState === 'idle' && (
        <>
          <span style={{ fontSize: 10, color: 'var(--queen)', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 10, fontWeight: 600 }}>
            Queen
          </span>
          <textarea
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Describe your goal…"
            style={{
              width: '100%',
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text)',
              fontSize: 11,
              resize: 'none',
              textAlign: 'center',
              fontFamily: 'inherit',
              lineHeight: 1.5,
            }}
            rows={4}
            autoFocus
          />
          <button
            onClick={handleSubmit}
            disabled={!draft.trim()}
            style={{
              marginTop: 8,
              padding: '5px 14px',
              background: draft.trim() ? 'var(--queen)' : 'transparent',
              border: '1px solid var(--queen)',
              borderRadius: 4,
              color: 'var(--text)',
              fontSize: 10,
              fontWeight: 600,
              cursor: draft.trim() ? 'pointer' : 'not-allowed',
              letterSpacing: 0.5,
              transition: 'all 0.2s',
            }}
          >
            ASK THE QUEEN
          </button>
        </>
      )}

      {appState === 'planning' && (
        <>
          <span style={{ fontSize: 10, color: 'var(--queen)', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 14, fontWeight: 600 }}>
            Queen
          </span>
          <div style={{
            width: 24, height: 24,
            border: '2px solid var(--queen)',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
            marginBottom: 10,
          }} />
          <span style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'center' }}>Planning…</span>
        </>
      )}

      {(appState === 'planned' || appState === 'running' || appState === 'done') && (
        <>
          <span style={{ fontSize: 10, color: 'var(--queen)', textTransform: 'uppercase', letterSpacing: 2, marginBottom: 8, fontWeight: 600 }}>
            Queen
          </span>
          <span style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.5, overflow: 'hidden' }}>
            {goal.length > 80 ? goal.slice(0, 80) + '…' : goal}
          </span>
        </>
      )}
    </div>
  )
}
