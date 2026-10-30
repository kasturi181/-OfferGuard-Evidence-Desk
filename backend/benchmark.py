"""Offline evaluation on synthetic labelled messages. No network, no database."""
import json
from pathlib import Path

import db
from checks.company_identity import check_company
from extract import extract_fields
from rules import assess, run_rules

FILE = Path(__file__).parent / "fixtures" / "benchmark.json"


def run_benchmark() -> dict:
    cases = json.loads(FILE.read_text())["cases"]
    companies = db.fixture_companies()
    rows, tp, fp, tn, fn = [], 0, 0, 0, 0
    for c in cases:
        fields = extract_fields(c["text"])
        checks = check_company(c["text"], fields, companies, "fixture")
        findings = run_rules(c["text"], fields, checks)
        found = [f["rule_id"] for f in findings if f["severity"] != "info"]
        level = assess(findings)["level"]
        flagged, scam = level != "none", c["label"] == "scam"
        tp, fp, tn, fn = tp + (flagged and scam), fp + (flagged and not scam), tn + (not flagged and not scam), fn + (not flagged and scam)
        rows.append({"id": c["id"], "label": c["label"], "text": c["text"], "expected": c["expect"], "found": found, "level": level,
                     "flagged": flagged, "correct": flagged == scam, "rules_ok": set(c["expect"]) <= set(found), "note": c.get("note", "")})
    n = len(rows)
    return {
        "total": n, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(tp / (tp + fp), 2) if tp + fp else None, "recall": round(tp / (tp + fn), 2) if tp + fn else None,
        "accuracy": round((tp + tn) / n, 2) if n else None,
        "note": "Synthetic, manually labelled messages. This measures the rules on examples we wrote, not real-world accuracy.",
        "cases": rows,
    }
