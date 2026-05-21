# COMB 🍯

**Collaborative Orchestration of Multi-agent Behavior**

COMB is an open-source CLI-first AI agent orchestration tool. You describe a goal in plain language. A **queen agent** breaks it down into a structured plan of specialized sub-agents — each with its own model and provider. A **runner** executes them in parallel and collects their outputs. A **web UI** visualizes the swarm as a honeycomb: the queen at the center, worker agents in a glowing ring around her.

---

## How it works

```
You: "Research and summarize the latest trends in edge computing"
         │
         ▼
  ┌─────────────┐
  │  Queen Agent │  ← picks model/provider from your stored keys
  └──────┬──────┘
         │ returns AgentPlan
         ▼
  ┌──────┴──────────────────────────────┐
  │  researcher   coder   analyst  ...  │  ← workers run in parallel
  └──────┬──────────────────────────────┘
         │ each calls complete(prompt, model, provider)
         ▼
      Results collected → printed / shown in UI
```

**Supported providers:** OpenAI · Anthropic · Gemini · Groq · Mistral · Ollama

---

## Quick start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Node.js 18+ (only for the web UI)
- API keys for the providers you want to use

### Install

```bash
git clone https://github.com/sankerathul/comb
cd comb
uv pip install -e .
```

### Store your API keys

```bash
comb add key openai     sk-...
comb add key anthropic  sk-ant-...
comb add key groq       gsk-...
```

Keys are stored in `~/.comb/.vault.env` with `0600` permissions — never inside your project.

### Run from the CLI

```bash
comb run "write a Python web scraper that extracts product prices"
```

```
Planning agents...
✓ Plan: 3 agents
  · researcher  (openai / gpt-4o-mini)
  · coder       (anthropic / claude-haiku-4-5)
  · reviewer    (groq / llama3-8b-8192)

Running agents in parallel...

━━━ coder  anthropic/claude-haiku-4-5 ━━━━━━━━━━━━━━━━━
[output]

━━━ researcher  openai/gpt-4o-mini ━━━━━━━━━━━━━━━━━━━━
[output]
...
```

### Run the web UI

```bash
# Terminal 1 — backend (defaults to port 1234)
comb serve --port 1234

# Terminal 2 — frontend dev server
cd web && npm install && npm run dev
# Open http://localhost:5173
```

Type a goal → the queen plans → ghost hexagons light up as named agents → click **Run Agents** → outputs fill each hex.

---

## CLI reference

```
comb add key <provider> <api-key>   Store an API key
comb list keys                      List all stored providers
comb remove key <provider>          Remove a stored API key

comb run "<goal>"                   Plan and execute a multi-agent swarm
comb serve [--host HOST]            Start the web UI backend
           [--port PORT]
```

**Override the queen's model at runtime:**

```bash
COMB_QUEEN_PROVIDER=openai COMB_QUEEN_MODEL=gpt-4o comb run "..."
```

---

## Project structure

```
comb/
├── cli.py                  Entry point — Typer commands
├── config.py               Global settings (pydantic-settings, env-var overrides)
├── constants.py            Provider enum + SUPPORTED_PROVIDERS list
│
├── vault/                  Credential storage
│   ├── backends/
│   │   ├── base.py         VaultBackend ABC (set / get / delete / list)
│   │   ├── dotenv.py       Default: ~/.comb/.vault.env, 0600 permissions
│   │   └── __init__.py     BACKENDS registry — add new backends here
│   └── vault.py            Singleton vault instance
│
├── providers/
│   └── provider.py         complete(prompt, model, provider) → str  via litellm
│
├── agents/
│   ├── queen.py            plan(goal) → AgentPlan  (AgentSpec list)
│   └── runner.py           run(AgentPlan) → list[AgentResult]  (parallel)
│
└── api/
    └── server.py           FastAPI — POST /api/plan, POST /api/run

web/                        React + Vite frontend
├── src/
│   ├── App.tsx             State machine: idle → planning → planned → running → done
│   ├── types.ts            TypeScript interfaces (AgentSpec, AgentPlan, AgentResult)
│   └── components/
│       ├── HoneycombGrid.tsx   Six-slot ring + connector lines
│       ├── QueenHex.tsx        Center hexagon — input / spinner / goal display
│       └── AgentHex.tsx        Worker hexagons — ghost / active / running / done
└── vite.config.ts          Proxies /api → backend port

tests/
├── test_vault.py           11 tests — vault CRUD, security, permissions
├── test_provider.py         6 tests — complete(), provider validation, vault wiring
├── test_queen.py            6 tests — plan(), JSON mode, error handling
└── test_runner.py           6 tests — parallel execution, failure isolation
```

---

## Developer guide

### Setup

```bash
uv pip install -e ".[dev]"   # installs comb + pytest + pytest-cov

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=comb --cov-report=term-missing
```

### Adding a new vault backend

1. Create `comb/vault/backends/yourbackend.py`, subclass `VaultBackend`, implement `set / get / delete / list`
2. Register it in `comb/vault/backends/__init__.py`:
   ```python
   BACKENDS = {
       "dotenv":      DotEnvBackend,
       "yourbackend": YourBackend,   # ← add here
   }
   ```
3. Select it at runtime: `COMB_VAULT_BACKEND=yourbackend comb add key openai sk-...`

### Adding a new provider

1. Add the provider to the `Provider` enum in `comb/constants.py`
2. That's it — `complete()` passes calls through litellm, which handles the provider automatically

### Configuring the queen

The queen's model and provider are set in `comb/config.py` and overridable via env vars:

| Setting | Env var | Default |
|---|---|---|
| Queen provider | `COMB_QUEEN_PROVIDER` | `anthropic` |
| Queen model | `COMB_QUEEN_MODEL` | `claude-opus-4-7` |
| Vault backend | `COMB_VAULT_BACKEND` | `dotenv` |
| Vault file path | `COMB_VAULT_ENV_FILE` | `~/.comb/.vault.env` |

### Git workflow

```
feat/* → dev → main
```

Branch protection is on both `main` and `dev`. PRs are required for all merges — never commit directly.

### Architecture notes

- **`from comb.vault import vault`** — the only import needed anywhere to access credentials. One singleton, backend-agnostic.
- **`complete(prompt, model, provider)`** — the only call needed to invoke any LLM. litellm handles routing.
- **`plan(goal)`** uses JSON mode (`response_format={"type": "json_object"}`) for reliable structured output.
- **`run(agent_plan)`** uses `ThreadPoolExecutor` — litellm calls are synchronous/blocking, threads are the right tool.
- **`AgentResult.error`** is never `None` AND `output` is never `None` at the same time — one always set, one always `None`.

---

## Roadmap

- [x] Vault — pluggable credential storage
- [x] Provider layer — unified `complete()` via litellm
- [x] Queen agent — natural language → structured AgentPlan
- [x] Agent runner — parallel execution with failure isolation
- [x] Web UI — honeycomb visualization
- [ ] Shared memory — SQLite-backed, swappable
- [ ] Streaming output — real-time hex fill as agents respond
- [ ] Additional vault backends — keyring, Infisical, HashiCorp Vault
