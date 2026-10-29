import json
import re
from datetime import datetime, timezone
from pathlib import Path

RECORDS = json.loads((Path(__file__).parent.parent / "fixtures" / "company_records.json").read_text())["records"]
SUFFIX = re.compile(r"\b(pvt|private|ltd|limited|llp|inc)\b")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", SUFFIX.sub("", re.sub(r"[^a-z0-9 ]", " ", s.lower()))).strip()


def check_company(text: str, fields: dict) -> dict:
    base = {"name": "company_identity", "source": "Synthetic sample dataset (NOT an official registry)",
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    t = norm(text)
    rec = next((r for r in RECORDS if norm(r["name"]) in t), None)
    if not rec:
        who = fields.get("company") or "company"
        return {**base, "status": "not_checked", "details": f"'{who}' not in sample dataset. Live registry check NOT performed."}
    emails = fields.get("recruiter_emails") or []
    if not emails:
        return {**base, "status": "not_checked", "details": f"Record found for {rec['name']} but no recruiter email to compare."}
    dom = emails[0].split("@")[-1].lower()
    if any(dom == d or dom.endswith("." + d) for d in rec["official_domains"]):
        return {**base, "status": "verified_match", "details": f"{dom} matches official domain of {rec['name']}. Does not prove recruiter is authorized."}
    return {**base, "status": "warning", "details": f"Recruiter domain '{dom}' differs from known official domain(s) {rec['official_domains']} for {rec['name']}."}
