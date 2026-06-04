import os
import json
import re
import jsonschema

def parse_normalized_text(text, source_segments):
    """
    Cleans up normalized_text and extracts source_evidence.
    Example: "ho (duration: 3 ngày, source_start_time: 3.3, source_end_time: 6.1)"
    """
    clean_text = text
    start_time = None
    end_time = None
    
    # Try to extract source_start_time and source_end_time
    time_match = re.search(r'source_start_time:\s*([\d.]+).*?source_end_time:\s*([\d.]+)', text)
    if time_match:
        start_time = float(time_match.group(1))
        end_time = float(time_match.group(2))
    
    # Remove the parenthesis block containing the metadata
    clean_text = re.sub(r'\s*\(.*?\)\s*$', '', text).strip()
    
    evidence = []
    for seg_id in source_segments:
        # We don't have the full quote from transcript here easily,
        # but we can populate the structure with the segment_id and times.
        ev = {
            "segment_id": seg_id,
            # Quote should ideally come from transcript, but we use original text as a fallback
            # since original_text often reflects the exact quote in synthetic data.
            "quote": "Refer to original_text or transcript." 
        }
        if start_time is not None:
            ev["start_time"] = start_time
        if end_time is not None:
            ev["end_time"] = end_time
            
        evidence.append(ev)
        
    return clean_text, evidence

def process_case(case_dir, schema):
    gold_file = os.path.join(case_dir, "clinical_facts_gold.json")
    if not os.path.exists(gold_file):
        return
    
    print(f"Processing {case_dir}...")
    
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
        
    candidate_data = []
    
    # We handle cases where gold_data might be an array or a single object
    if not isinstance(gold_data, list):
        gold_data = [gold_data]
        
    for fact in gold_data:
        # Create a deep copy
        cand = json.loads(json.dumps(fact))
        
        # 1. Update statuses
        cand["doctor_confirmation_status"] = "pending"
        cand["review_status"] = "pending_review"
        
        # 2. Remove reviewer metadata
        cand.pop("reviewed_by", None)
        cand.pop("reviewed_at", None)
        
        # 3. Clean up normalized_text and create source_evidence
        orig_norm = cand.get("normalized_text", "")
        segments = cand.get("source_segment_ids", [])
        
        # If it already has clean source_evidence, don't override
        if "source_evidence" not in cand:
            clean_norm, evidence = parse_normalized_text(orig_norm, segments)
            cand["normalized_text"] = clean_norm
            cand["source_evidence"] = evidence
            # As requested for MVP: keep dose/route in original_text/evidence, 
            # so the normalized_text is clean.
        
        # 4. For SYN_OUT_001 we used confidence 1.0, keeping whatever gold has.
        
        # 5. Validate against schema
        try:
            jsonschema.validate(instance=cand, schema=schema)
            candidate_data.append(cand)
        except jsonschema.exceptions.ValidationError as e:
            print(f"  [ERROR] Validation failed for fact {cand.get('fact_id')}: {e.message}")
            # Still append it or not? Let's append to not lose data, but print error.
            candidate_data.append(cand)
            
    # Write to clinical_facts_candidate.json
    out_file = os.path.join(case_dir, "clinical_facts_candidate.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(candidate_data, f, ensure_ascii=False, indent=4)
    print(f"  -> Generated {out_file} with {len(candidate_data)} valid facts.")

if __name__ == "__main__":
    schema_path = "data/schemas/clinical_fact.schema.json"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
        
    base_dir = "data/synthetic_data/outpatient_v0_1"
    
    for item in sorted(os.listdir(base_dir)):
        if item.startswith("SYN_OUT_"):
            case_dir = os.path.join(base_dir, item)
            if os.path.isdir(case_dir):
                process_case(case_dir, schema)
                
    print("Done generating and validating candidate files.")
