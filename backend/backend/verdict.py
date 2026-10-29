"""Deterministic, auditable verdict. No network, no LLM, no randomness.

compute_verdict(findings, consistency, checks) -> dict

Rules (all visible in `basis`):
  points: strong 40, medium 15, weak 5, info 0, consistency mismatch 8
  likely_fraudulent : any strong finding, or score >= 60
  suspicious        : score >= 20
  low_risk          : otherwise
Confidence is lowered one step when any external check was unavailable.
low_risk confidence is always "limited": absence of signals is not verification.
"""
from __future__ import annotations

WEIGHTS = {"strong": 40, "medium": 15, "weak": 5, "info": 0}
MISMATCH_POINTS = 8
FRAUD_SCORE, SUSPICIOUS_SCORE = 60, 20

LABELS = {
    "likely_fraudulent": "Likely fraudulent",
    "suspicious": "Suspicious",
    "low_risk": "Low risk: no strong warning signs found",
}
DISCLAIMER = (
    "This is a risk assessment from rule-based warning signs, not a legal determination "
    "and not proof either way. Always verify the employer through a trusted channel "
    "before paying money or sharing documents."
)
_STEP = ["limited", "moderate", "high"]


def _sev(f) -> str:
    s = str((f or {}).get("severity", "info")).lower()
    return s if s in WEIGHTS else "info"


def _name(f) -> str:
    return str(f.get("title") or f.get("rule") or f.get("claim") or f.get("id") or "signal")


def compute_verdict(findings, consistency=None, checks=None) -> dict:
    basis, score = [], 0
    strong_with_evidence = 0
    for f in findings or []:
        if not isinstance(f, dict):
            continue
        sev = _sev(f)
        pts = WEIGHTS[sev]
        score += pts
        if sev == "strong" and (f.get("matched_text") or f.get("evidence")):
            strong_with_evidence += 1
        basis.append({"source": "finding", "name": _name(f), "severity": sev, "points": pts})
    for c in consistency or []:
        if c.get("status") == "mismatch":
            score += MISMATCH_POINTS
            basis.append({"source": "consistency", "name": c.get("check", "consistency"),
                          "severity": "medium", "points": MISMATCH_POINTS})
    score = min(score, 100)

    has_strong = any(b["severity"] == "strong" for b in basis)
    if has_strong or score >= FRAUD_SCORE:
        key = "likely_fraudulent"
        conf = "high" if strong_with_evidence else "moderate"
    elif score >= SUSPICIOUS_SCORE:
        key, conf = "suspicious", "moderate"
    else:
        key, conf = "low_risk", "limited"

    unavailable = [c for c in (checks or []) if c.get("status") == "unavailable"]
    not_checked = [c for c in (checks or []) if c.get("status") == "not_checked"]
    if unavailable and key != "low_risk":
        conf = _STEP[max(0, _STEP.index(conf) - 1)]

    unverified = []
    for c in unavailable + not_checked:
        unverified.append(f"{c.get('name') or c.get('id') or 'check'}: "
                          f"{'could not run' if c in unavailable else 'not checked'}")
    for c in consistency or []:
        if c.get("status") == "not_checked":
            unverified.append(f"{c.get('check')}: not checked")
    unverified.append("Recruiter authorization and vacancy existence are never verified by this tool.")

    top = sorted([b for b in basis if b["points"] > 0], key=lambda b: -b["points"])[:3]
    if key == "low_risk":
        summary = ("No strong or multiple warning signs were found in the text and checks that ran. "
                   "That does not mean the offer is genuine.")
        if top:
            summary += " Minor signals: " + "; ".join(b["name"] for b in top) + "."
    else:
        why = "; ".join(f"{b['name']} ({b['severity']})" for b in top)
        summary = (f"Strong warning sign found: {why}." if key == "likely_fraudulent" and has_strong
                   else f"Several warning signs add up: {why}.")

    return {"verdict": key, "label": LABELS[key], "summary": summary, "score": score,
            "max_score": 100, "confidence": conf, "basis": basis,
            "unverified": unverified, "disclaimer": DISCLAIMER}
