export interface AgentSpec {
  role: string
  model: string
  provider: string
}

export interface AgentPlan {
  goal: string
  agents: AgentSpec[]
}

export interface AgentResult {
  role: string
  model: string
  provider: string
  output: string | null
  error: string | null
}

export type AppState = 'idle' | 'planning' | 'planned' | 'running' | 'done'
