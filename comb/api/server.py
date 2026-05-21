from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from comb.agents import plan, run
from comb.agents.queen import AgentPlan

app = FastAPI(title="COMB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    goal: str


@app.post("/api/plan")
def api_plan(body: PlanRequest):
    try:
        return plan(body.goal).model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/run")
def api_run(agent_plan: AgentPlan):
    results = run(agent_plan)
    return [r.model_dump() for r in results]


# Serve built frontend if web/dist exists
_dist = Path(__file__).parent.parent.parent / "web" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")
