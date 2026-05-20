# COMB 🍯

**Collaborative Orchestration of Multi-agent Behavior**

COMB is an open-source AI agent orchestration tool. Describe a goal, and COMB spins up a collaborative swarm of specialized AI agents — each with its own model, role, and memory — that work together to get it done.

## How it works

- A **queen agent** interprets your goal and spawns the right agents for the job
- Each **worker agent** can use any AI provider and model independently
- All agents share a common **memory layer** so context is never lost
- You have full control — inspect, edit, or override any agent at any time

## Status

🚧 Early development — CLI foundation in progress.

## Quick start

```bash
# install
pip install comb   # coming soon

# run
comb --help
```

## Roadmap

- [ ] Credential vault (multi-provider API key management)
- [ ] Provider layer (OpenAI, Anthropic, Gemini)
- [ ] Queen agent (goal → agent plan)
- [ ] Agent runner (parallel execution)
- [ ] Shared memory layer
- [ ] Web UI

## License

MIT