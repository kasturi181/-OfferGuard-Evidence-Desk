"""One call that adds everything new to an existing report.

    from enrich import enrich_report
    report = await enrich_report(report, text, simulate_failure=body.simulate_url_failure)

Adds (all additive, old keys untouched):
  consistency, checks (+domain_age, +registry), findings (+weak domain-age finding),
  verdict_detail, checklist, guidance, ai_explanation (optional).
Rules and verdict stay deterministic. LLM output is labelled and never scored.
"""
from __future__ import annotations
import asyncio
import logging

from checklist import build_checklist
from checks.consistency import check_consistency, FREE_MAIL
from checks.domain_age import check_domain_age
from checks.registry import check_registry
from guidance import build_guidance
from verdict import compute_verdict
import llm_explain

log = logging.getLogger("offerguard.enrich")


def _first_corporate_domain(fields: dict) -> str | None:
    for e in fields.get("emails") or fields.get("recruiter_emails") or []:
        d = e.rsplit("@", 1)[-1].lower() if "@" in e else ""
        if d and d not in FREE_MAIL:
            return d
    return None


async def enrich_report(report: dict, text: str, *, simulate_failure: bool = False,
                        use_llm: bool = True) -> dict:
    if hasattr(report, "model_dump"):
        report = report.model_dump()
    fields = dict(report.get("extracted_fields") or {})

    # optional LLM extraction: fills missing keys only, values verified against the text
    if use_llm and llm_explain.enabled():
        extra = await llm_explain.extract_fields_llm(text)
        for k, v in (extra or {}).items():
            if not fields.get(k):
                fields[k] = v
        report["extracted_fields"] = fields

    # external checks in parallel; each one never raises
    domain = _first_corporate_domain(fields)
    age, registry = await asyncio.gather(
        check_domain_age(domain, simulate_failure),
        check_registry(fields.get("company_name"), simulate_failure))
    checks = list(report.get("checks") or [])
    checks += [age, registry]
    report["checks"] = checks

    findings = list(report.get("findings") or [])
    if age["status"] == "warning":  # weak signal (brief: recently created website)
        findings.append({
            "id": "recent_domain", "title": "Recently registered company website", "severity": "weak",
            "matched_text": age["domain"], "source": age["source"], "status": "warning",
            "why": age["detail"], "unverified": "Whether the company is new or the domain was moved is unknown.",
            "confidence": "low", "next_action": "Compare with the official site found by searching the company name."})
    report["findings"] = findings

    consistency = check_consistency(fields)
    report["consistency"] = consistency

    v = compute_verdict(findings, consistency, checks)
    report["verdict_detail"] = v
    report["verdict"] = v["verdict"]
    report["checklist"] = build_checklist(findings, fields)
    report["guidance"] = build_guidance(fields, v["verdict"])

    missing = list(report.get("missing_checks") or [])
    for u in v["unverified"]:
        if u not in missing:
            missing.append(u)
    report["missing_checks"] = missing

    report["ai_explanation"] = None
    if use_llm:
        try:
            report["ai_explanation"] = await llm_explain.explain_plain(report)
        except Exception:
            log.exception("explain failed")
    return report
