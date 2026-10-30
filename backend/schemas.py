from typing import Literal, Optional
from pydantic import BaseModel, Field


class AnalyzeIn(BaseModel):
    text: str
    simulate_url_failure: bool = False


class ReportIn(BaseModel):
    kind: Literal["email", "domain", "company", "phone"]
    value: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=500)


class Finding(BaseModel):
    rule_id: str
    severity: str  # strong | medium | weak | info
    title: str
    claim: str
    evidence: str
    start: Optional[int] = None
    end: Optional[int] = None
    source: str
    why: str
    status: str
    uncertainty: str
    action: str


class Check(BaseModel):
    name: str
    status: str  # verified_match | warning | no_match | unavailable | not_checked
    source: str
    checked_at: str
    details: str
    count: int = 0  # community check: number of matching reports (drives severity)


class Report(BaseModel):
    extracted_fields: dict
    findings: list[Finding]
    checks: list[Check]
    assessment: dict
    missing_checks: list[str]
    limitations: list[str]
    checklist: list[dict] = []
    analyzed_text: str = ""
    explain: dict = {}
    drafts: list[dict] = []
    mode: str = "backend"
