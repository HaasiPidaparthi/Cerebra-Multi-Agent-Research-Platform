import json
from typing import Optional
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from engine.schemas.planner import ResearchPlan

PLANNER_SYSTEM = """You are a senior strategy analyst and research planner.
Your job: turn a vague business question into a research plan that can produce a concise, defensible brief.

Rules:
- Subquestions must cover: market, users/buyers, competitors/alternatives, economics/pricing, risks (regulatory/operational), and execution considerations.
- Search queries must be specific and diverse (mix market sizing, competitor docs, analyst reports, regulatory sources, and credible news).
- Keep it tool-friendly: queries should be copy/paste ready.
- Include assumptions explicitly if the question is underspecified.
- Keep scope realistic: do not propose more work than needed.
"""

PLANNER_HUMAN = """Question: {question}

Constraints:
- Budget (USD est): {budget_usd}
- Time limit (seconds): {time_limit_s}

Return a ResearchPlan.
"""

def _coerce_to_text(x) -> str:
    """Handle either AIMessage/BaseMessage or plain strings."""
    return x.content if hasattr(x, "content") else str(x)

def build_planner_runnable(llm: BaseChatModel) -> Runnable:
    """
    Returns a runnable that maps {question, budget_usd, time_limit_s} -> ResearchPlan
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", PLANNER_SYSTEM), ("human", PLANNER_HUMAN)]
    )
    # Path A: production models that support structured output
    try:
        structured_llm = llm.with_structured_output(ResearchPlan)
        return prompt | structured_llm
    except NotImplementedError:
        # Path B: fallback to unstructured output + manual parsing
        parser = PydanticOutputParser(pydantic_object=ResearchPlan)

        def _parse_to_plan(msg) -> ResearchPlan:
            text = _coerce_to_text(msg)

            # Prefer strict JSON parsing so tests stay deterministic
            data = json.loads(text)
            return ResearchPlan.model_validate(data)

        return prompt | llm | RunnableLambda(_parse_to_plan)

@dataclass
class PlannerAgent:
    llm: BaseChatModel

    def plan(self, question: str, budget_usd: float, time_limit_s: Optional[int] = None) -> ResearchPlan:
        runnable = build_planner_runnable(self.llm)
        return runnable.invoke(
            {
                "question": question,
                "budget_usd": budget_usd,
                "time_limit_s": time_limit_s or 0,
            }
        )