from typing import Optional
from pydantic import BaseModel


class AnalyzeIn(BaseModel):
    text: str
    simulate_url_failure: bool = False


class Finding(BaseModel):
    rule_id: str
    severity: str  # strong | medium | weak
    title: str
    claim: str
    evidence: str
    start: Optional[int] = None
    end: Optional[int] = None
    source: str
    why: str
    status: str  # matched_rule | warning | unavailable
    uncertainty: str
    action: str


class Check(BaseModel):
    name: str
    status: str  # verified_match | warning | no_match | unavailable | not_checked
    source: str
    checked_at: str
    details: str


class Report(BaseModel):
    extracted_fields: dict
    findings: list[Finding]
    checks: list[Check]
    assessment: dict
    missing_checks: list[str]
    limitations: list[str]
    mode: str = "backend"
