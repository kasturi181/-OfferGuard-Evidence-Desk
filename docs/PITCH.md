# OfferGuard Evidence Desk: one-page pitch
(Edit the [brackets], then paste into Google Docs or Slides and export as PDF.)

**Problem.** Fake job offers ask students and freshers for registration fees, OTPs and documents. People have no quick way to see what is suspicious or why.

**Solution.** Paste an offer, upload a text PDF or upload a screenshot. OfferGuard returns an evidence report: which warning signs were found, the exact words behind each one, what could not be verified, and what to do next. It does not claim to prove an offer is genuine or fake.

**What makes it different**
1. Evidence, not a black-box score. Every finding links to the exact text, the source and the uncertainty.
2. Cross-source checks. Recruiter email domain, links, registration number (CIN) and location are each compared with the company's record.
3. Honest about gaps. A check that could not run is shown as "not checked", never as "safe".
4. Actionable. A tailored checklist, ready-to-send verification messages, and notes for a cybercrime report (cybercrime.gov.in / 1930).
5. Measured. 20 labelled synthetic cases: 90% precision, 90% recall, with the failures shown.
6. Private. Offer text is not stored. Screenshots are read on the user's own device.

**How it works.** React + Vite frontend (Vercel) → FastAPI backend (Render) → field extraction → 14 deterministic rules + cross-source checks + optional Google Safe Browsing → evidence report. If the backend is down, a reduced local rule set runs and is clearly labelled.

**Limits (stated openly).** Warning signs are not proof. Company records are a small synthetic sample, not an official registry. Scanned PDFs need the screenshot upload. Rules cover common patterns, so new scam wording can be missed.

**Next steps.** Live registry lookup, more languages, evidence highlighting for PDFs, user accounts and history, browser extension.

**Links.** Live: [https://offerguard-psi.vercel.app] · Code: [GitHub link] · Video: [link] · Author: [your name]
