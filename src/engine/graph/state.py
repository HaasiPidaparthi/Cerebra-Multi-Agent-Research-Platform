from typing import TypedDict
from engine.schemas.planner import ResearchPlan

class WorkflowState(TypedDict, total=False):
    question: str
    budget_usd: float
    time_limit_s: int
    plan: ResearchPlan