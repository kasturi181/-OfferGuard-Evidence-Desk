"""Plain-language summary in English and Hindi. Deterministic (no LLM)."""

LEVEL = {
    "high": ("This offer shows {n} strong warning sign(s). Do not pay money or share documents until you have verified the employer yourself.",
             "इस ऑफ़र में {n} गंभीर चेतावनी संकेत मिले हैं। जब तक आप कंपनी की खुद जाँच न कर लें, पैसे न दें और दस्तावेज़ साझा न करें।"),
    "elevated": ("This offer shows several warning signs. Verify the employer through official channels before you continue.",
                 "इस ऑफ़र में कई चेतावनी संकेत मिले हैं। आगे बढ़ने से पहले कंपनी की आधिकारिक माध्यम से जाँच करें।"),
    "some": ("A few warning signs were found. Check them before you go ahead.",
             "कुछ चेतावनी संकेत मिले हैं। आगे बढ़ने से पहले उन्हें जाँच लें।"),
    "none": ("Our rules found no warning signs. This does not prove the offer is genuine, so still verify the company.",
             "हमारे नियमों को कोई चेतावनी संकेत नहीं मिला। इसका मतलब यह नहीं कि ऑफ़र असली है, इसलिए कंपनी की जाँच ज़रूर करें।"),
}
LINES = {
    "RULE-01": ("They ask you to pay money to get the job. Real employers do not charge candidates.", "नौकरी पाने के लिए पैसे माँगे जा रहे हैं। असली कंपनियाँ उम्मीदवारों से पैसे नहीं लेतीं।"),
    "RULE-02": ("They ask for your OTP, PIN or password. Never share these with anyone.", "OTP, PIN या पासवर्ड माँगा जा रहा है। इन्हें कभी किसी को न बताएँ।"),
    "RULE-03": ("A link in the message is flagged as dangerous.", "संदेश में दिया गया लिंक खतरनाक के रूप में चिह्नित है।"),
    "RULE-04": ("The recruiter's email domain does not match the company's official website.", "रिक्रूटर का ईमेल डोमेन कंपनी की आधिकारिक वेबसाइट से मेल नहीं खाता।"),
    "RULE-05": ("The recruiter uses a personal email such as Gmail instead of a company email.", "रिक्रूटर कंपनी के ईमेल की जगह Gmail जैसा निजी ईमेल इस्तेमाल कर रहा है।"),
    "RULE-06": ("They want your Aadhaar, PAN or bank details too early.", "वे बहुत जल्दी आपका आधार, पैन या बैंक विवरण माँग रहे हैं।"),
    "RULE-07": ("They promise selection or push you to act fast.", "वे चयन की गारंटी दे रहे हैं या जल्दबाज़ी करवा रहे हैं।"),
    "RULE-08": ("The salary is far above normal for this kind of job.", "इस तरह की नौकरी के लिए वेतन सामान्य से बहुत ज़्यादा बताया गया है।"),
    "RULE-09": ("They move you to Telegram, WhatsApp or a form.", "वे आपको टेलीग्राम, व्हाट्सऐप या किसी फ़ॉर्म पर ले जा रहे हैं।"),
    "RULE-10": ("We could not confirm that the company or recruiter is real.", "हम यह पुष्टि नहीं कर सके कि कंपनी या रिक्रूटर असली है।"),
    "RULE-11": ("A link in the offer does not belong to the company's website.", "ऑफ़र में दिया गया लिंक कंपनी की वेबसाइट का नहीं है।"),
    "RULE-12": ("The company registration number (CIN) does not match our record.", "कंपनी का पंजीकरण नंबर (CIN) हमारे रिकॉर्ड से मेल नहीं खाता।"),
    "RULE-13": ("The job location differs from the company's recorded office.", "नौकरी की जगह कंपनी के दर्ज कार्यालय से अलग है।"),
    "RULE-14": ("Other users reported similar details (unverified).", "अन्य उपयोगकर्ताओं ने ऐसी ही जानकारी की शिकायत की है (असत्यापित)।"),
}
NEXT = [
    ("Check the company yourself on its official website and the MCA portal.", "कंपनी की आधिकारिक वेबसाइट और MCA पोर्टल पर खुद जाँच करें।"),
    ("Do not pay anything and do not share documents or OTPs.", "पैसे न दें और दस्तावेज़ या OTP साझा न करें।"),
]
LOST = ("If you already lost money, call 1930 and report at cybercrime.gov.in.", "अगर पैसे जा चुके हैं तो 1930 पर कॉल करें और cybercrime.gov.in पर शिकायत करें।")


def build_explanation(findings: list[dict], assessment: dict) -> dict:
    sig = [f for f in findings if f["severity"] != "info"]
    n = assessment["counts"]["strong"]
    top = sig[:4] if sig else [f for f in findings][:1]
    nxt = list(NEXT) + ([LOST] if any(f["severity"] in ("strong", "medium") for f in findings) else [])
    out = {}
    for i, lang in enumerate(("en", "hi")):
        out[lang] = {
            "summary": LEVEL[assessment["level"]][i].format(n=n),
            "points": [LINES[f["rule_id"]][i] for f in top if f["rule_id"] in LINES],
            "next": [x[i] for x in nxt],
        }
    return out
