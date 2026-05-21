import { AgentPlan, AgentResult, AppState } from '../types'
import { AgentHex } from './AgentHex'
import { QueenHex } from './QueenHex'

interface Props {
  appState: AppState
  goal: string
  plan: AgentPlan | null
  results: AgentResult[]
  onSubmit: (goal: string) => void
}

// 6 ring slots at 60° increments, starting from top
const RING_ANGLES_DEG = [-90, -30, 30, 90, 150, 210]
const RING_RADIUS = 265

function hexPosition(angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180
  return {
    x: Math.round(RING_RADIUS * Math.cos(rad)),
    y: Math.round(RING_RADIUS * Math.sin(rad)),
  }
}

export function HoneycombGrid({ appState, goal, plan, results, onSubmit }: Props) {
  const SIZE = 700
  const CX = SIZE / 2
  const CY = SIZE / 2

  return (
    <div
      style={{
        width: SIZE,
        height: SIZE,
        position: 'relative',
        flexShrink: 0,
      }}
    >
      {/* Queen at center */}
      <div
        style={{
          position: 'absolute',
          left: CX - 110,
          top: CY - 127,
        }}
      >
        <QueenHex appState={appState} goal={goal} onSubmit={onSubmit} />
      </div>

      {/* Six ring slots */}
      {RING_ANGLES_DEG.map((angle, i) => {
        const { x, y } = hexPosition(angle)
        const spec = plan?.agents[i]
        const result = results.find(r => r.role === spec?.role)

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: CX + x - 80,
              top: CY + y - 92,
              transition: 'opacity 0.4s ease',
            }}
          >
            <AgentHex
              spec={spec}
              result={result}
              appState={appState}
              index={i}
            />
          </div>
        )
      })}

      {/* Connector lines from queen to active agents */}
      <svg
        style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
        width={SIZE}
        height={SIZE}
      >
        {plan?.agents.map((agent, i) => {
          const { x, y } = hexPosition(RING_ANGLES_DEG[i])
          return (
            <line
              key={agent.role}
              x1={CX}
              y1={CY}
              x2={CX + x}
              y2={CY + y}
              stroke="rgba(217,119,6,0.2)"
              strokeWidth={1}
              strokeDasharray="4 4"
            />
          )
        })}
      </svg>
    </div>
  )
}
