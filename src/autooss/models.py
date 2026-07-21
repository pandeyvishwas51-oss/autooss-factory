from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrendSignal(BaseModel):
    source: str  # hn | github | reddit | seed
    title: str
    url: str = ""
    score: float = 0.0
    tags: List[str] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict)


class Opportunity(BaseModel):
    id: str
    name: str
    one_liner: str
    problem: str
    solution: str
    skill_tags: List[str] = Field(default_factory=list)
    domain: str = "ai-ml-scraping"  # ai | scraping | rag | reverse-eng | ml
    novelty_score: float = 0.0
    demand_score: float = 0.0
    feasibility_score: float = 0.0
    portfolio_score: float = 0.0
    total_score: float = 0.0
    related_signals: List[str] = Field(default_factory=list)
    mvp_modules: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def rank_key(self) -> float:
        return self.total_score


class DailyRunReport(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    signals_count: int = 0
    opportunities: List[Opportunity] = Field(default_factory=list)
    scaffolded: List[str] = Field(default_factory=list)
    pushed: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
