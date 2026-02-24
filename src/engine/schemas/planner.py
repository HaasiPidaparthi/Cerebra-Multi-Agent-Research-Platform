from typing import List, Optional
from pydantic import BaseModel, Field

class StopCriteria(BaseModel):
    min_sources: int = Field(default=8, ge=1, description="Minimum distinct sources to collect")
    min_claim_coverage: float = Field(
        default=0.85, ge=0.0, le=1.0, description="Fraction of claims supported by evidence"
    )
    max_minutes: Optional[int] = Field(
        default=None, ge=1, description="Optional time cap for research stage"
    )

class ResearchPlan(BaseModel):
    subquestions: List[str] = Field(min_length=3, max_length=12)
    search_queries: List[str] = Field(min_length=5, max_length=20)
    stop_criteria: StopCriteria = Field(default_factory=StopCriteria)
    assumptions: List[str] = Field(default_factory=list)
    risks_to_check: List[str] = Field(default_factory=list)