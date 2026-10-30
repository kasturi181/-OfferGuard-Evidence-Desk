// Fictional / synthetic examples only.
export const demoCases = [
  { label: "Suspicious: fee + personal email", text: "Hello, we at Contoso Analytics Limited are hiring freshers. Your selection is confirmed. Pay a refundable registration fee of ₹2,000 today to secure your seat. Contact HR: contoso.hr@gmail.com. Join our Telegram group for updates." },
  { label: "Real company, look-alike domain", text: "Offer letter from Northwind Tech Pvt Ltd (CIN U11111MH2000PTC000001). Location: Pune. Please send your Aadhaar card and bank details within 24 hours. Apply at https://northwind-careers.com/apply. Reply to hr@northwind-careers.com." },
  { label: "Benign-looking", text: "Hi, thanks for applying to Northwind Tech Pvt Ltd (CIN U72900KA2015PTC123456), Bengaluru. Interview is Monday 10am. Details from hr@northwindtech.example." },
  { label: "Malicious URL test", text: "Apply here: http://testsafebrowsing.appspot.com/s/malware.html and share your OTP to confirm." },
];
export const sampleStats = {
  enabled: false, sample: true, companies_in_dataset: 3, total_analyses: 128,
  by_level: { high: 41, elevated: 27, some: 38, none: 22 },
  top_rules: [{ rule_id: "RULE-01", count: 38 }, { rule_id: "RULE-05", count: 31 }, { rule_id: "RULE-09", count: 24 }, { rule_id: "RULE-04", count: 19 }, { rule_id: "RULE-06", count: 12 }, { rule_id: "RULE-02", count: 9 }],
  daily: [14, 19, 11, 22, 25, 17, 20].map((count, i) => ({ date: `Day ${i + 1}`, count })),
  scam_reports: { total: 3, by_kind: { email: 1, domain: 1, phone: 1 }, recent: [
    { kind: "email", value: "pa***@fake-hiring.example", description: "Sample: asked for a registration fee", created_at: "sample" },
    { kind: "domain", value: "northwind-careers.com", description: "Sample: look-alike of a real company domain", created_at: "sample" } ] },
};
export const RULE_NAMES = {
  "RULE-01": "Upfront payment", "RULE-02": "OTP / credentials", "RULE-03": "Flagged URL", "RULE-04": "Email domain mismatch", "RULE-05": "Personal email",
  "RULE-06": "Documents too early", "RULE-07": "Pressure / guarantee", "RULE-08": "Implausible salary", "RULE-09": "Chat / form redirect",
  "RULE-10": "Unverified company", "RULE-11": "Link domain mismatch", "RULE-12": "Registration ID mismatch", "RULE-13": "Location mismatch", "RULE-14": "User reports match", "RULE-15": "New website",
};
