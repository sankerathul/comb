import { AgentResult, AgentSpec, AppState } from '../types'

interface Props {
  spec?: AgentSpec
  result?: AgentResult
  appState: AppState
  index: number
}

const HEX_CLIP = 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'

export function AgentHex({ spec, result, appState, index }: Props) {
  const isGhost = !spec
  const isRunning = appState === 'running' && spec && !result
  const isDone = !!result

  const baseStyle: React.CSSProperties = {
    width: 160,
    height: 185,
    clipPath: HEX_CLIP,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '28px 16px',
    position: 'relative',
    transition: 'all 0.5s ease',
    cursor: 'default',
  }

  if (isGhost) {
    return (
      <div
        style={{
          ...baseStyle,
          background: `linear-gradient(var(--bg), var(--bg)) padding-box,
                       linear-gradient(var(--ghost), var(--ghost)) border-box`,
          border: '1.5px dashed var(--ghost)',
          animation: `ghost-pulse ${2 + index * 0.3}s ease-in-out infinite`,
          clipPath: 'none',
        }}
        aria-hidden
      />
    )
  }

  if (isDone) {
    const hasError = !!result.error
    return (
      <div
        style={{
          ...baseStyle,
          background: hasError
            ? 'rgba(239,68,68,0.18)'
            : 'rgba(217,119,6,0.22)',
          boxShadow: hasError
            ? '0 0 18px 4px rgba(239,68,68,0.25)'
            : '0 0 18px 4px var(--worker-glow)',
          animation: 'fade-in 0.4s ease',
          overflow: 'hidden',
        }}
      >
        <span style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
          {spec!.provider}
        </span>
        <span style={{ fontSize: 13, fontWeight: 700, color: hasError ? 'var(--error)' : 'var(--worker)', textAlign: 'center', marginBottom: 6 }}>
          {spec!.role}
        </span>
        <div style={{
          fontSize: 9,
          color: 'var(--text-muted)',
          textAlign: 'center',
          lineHeight: 1.4,
          overflow: 'hidden',
          maxHeight: 72,
          maskImage: 'linear-gradient(to bottom, black 60%, transparent 100%)',
        }}>
          {hasError ? result.error : result.output}
        </div>
      </div>
    )
  }

  if (isRunning) {
    return (
      <div
        style={{
          ...baseStyle,
          background: 'rgba(217,119,6,0.1)',
          animation: 'run-pulse 1.4s ease-in-out infinite',
        }}
      >
        <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
          {spec.provider}
        </span>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--worker)', textAlign: 'center', marginBottom: 10 }}>
          {spec.role}
        </span>
        <div style={{
          width: 18, height: 18,
          border: '2px solid var(--worker)',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
    )
  }

  // planned — lit up, not yet running
  return (
    <div
      style={{
        ...baseStyle,
        background: 'rgba(217,119,6,0.13)',
        boxShadow: '0 0 12px 2px var(--worker-glow)',
        animation: 'fade-in 0.4s ease',
      }}
    >
      <span style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
        {spec.provider}
      </span>
      <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--worker)', textAlign: 'center', marginBottom: 4 }}>
        {spec.role}
      </span>
      <span style={{ fontSize: 9, color: 'var(--text-muted)', textAlign: 'center' }}>
        {spec.model}
      </span>
    </div>
  )
}
