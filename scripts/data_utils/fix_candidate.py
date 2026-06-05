import json

file_path = "data/synthetic_data/outpatient_v0_1/SYN_OUT_002/clinical_facts_candidate.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for fact in data:
    if "source_evidence" in fact:
        for ev in fact["source_evidence"]:
            if ev.get("quote") == "Refer to original_text or transcript.":
                ev["quote"] = fact.get("original_text", "")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
