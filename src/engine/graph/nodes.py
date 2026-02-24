from typing import Any, Dict
from langchain_core.runnables import RunnableConfig

from engine.agents.planner import PlannerAgent
from engine.graph.state import WorkflowState

def planner_node(agent: PlannerAgent):
    """
    Returns a LangGraph-compatible node function.
    """
    def _node(state: WorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        question = state["question"]
        budget_usd = float(state.get("budget_usd", 2.5))
        time_limit_s = int(state.get("time_limit_s", 0))

        plan = agent.plan(question=question, budget_usd=budget_usd, time_limit_s=time_limit_s)
        return {"plan": plan}

    return _node