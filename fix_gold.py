import json
import re

file_path = "data/synthetic_data/outpatient_v0_1/SYN_OUT_002/clinical_facts_gold.json"
transcript_path = "data/synthetic_data/outpatient_v0_1/SYN_OUT_002/transcript_segments_gold.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(transcript_path, "r", encoding="utf-8") as f:
    transcript = json.load(f)

segment_map = {seg["segment_id"]: seg for seg in transcript}

for fact in data:
    # 1. Clean normalized_text
    norm_text = fact.get("normalized_text", "")
    
    # Extract duration if present
    dur_match = re.search(r"duration:\s*([^,]+)", norm_text)
    
    # Remove the whole parenthesis block
    clean_text = re.sub(r"\s*\(.*?\)", "", norm_text).strip()
    
    # Append duration if it makes sense and isn't already in the text
    if dur_match:
        dur_val = dur_match.group(1).strip()
        if dur_val not in clean_text:
            clean_text = f"{clean_text} {dur_val}"
            
    fact["normalized_text"] = clean_text
    
    # 2. Add source_evidence
    if "source_segment_ids" in fact and "source_evidence" not in fact:
        evidence_list = []
        for seg_id in fact["source_segment_ids"]:
            if seg_id in segment_map:
                seg = segment_map[seg_id]
                evidence_list.append({
                    "segment_id": seg_id,
                    "quote": seg["text"],
                    "start_time": seg["start_time"],
                    "end_time": seg["end_time"]
                })
        fact["source_evidence"] = evidence_list

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
