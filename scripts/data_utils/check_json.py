import os
import json

base_dir = "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/synthetic_data/outpatient_v0_1"
ref_dir = os.path.join(base_dir, "SYN_OUT_001")

def get_structure(data):
    if isinstance(data, dict):
        return {k: get_structure(v) for k, v in data.items()}
    elif isinstance(data, list):
        if len(data) > 0:
            return [get_structure(data[0])]
        else:
            return []
    else:
        return type(data).__name__

targets = ["SYN_OUT_003", "SYN_OUT_004", "SYN_OUT_005", "SYN_OUT_006"]
json_files = ["encounter_metadata.json", "transcript_segments_gold.json", "clinical_facts_gold.json", "clinical_facts_candidate.json", "encounter_outcome.json", "soap_source_evidence.json"]

all_match = True

for target in targets:
    target_dir = os.path.join(base_dir, target)
    print(f"\n--- Checking {target} ---")
    for jfile in json_files:
        ref_path = os.path.join(ref_dir, jfile)
        tgt_path = os.path.join(target_dir, jfile)
        
        if not os.path.exists(tgt_path):
            print(f"❌ Missing: {jfile}")
            all_match = False
            continue
            
        with open(ref_path, "r", encoding="utf-8") as f:
            ref_data = json.load(f)
        with open(tgt_path, "r", encoding="utf-8") as f:
            tgt_data = json.load(f)
            
        ref_struct = get_structure(ref_data)
        tgt_struct = get_structure(tgt_data)
        
        if ref_struct == tgt_struct:
            print(f"✅ {jfile}: Format matches SYN_OUT_001.")
        else:
            print(f"⚠️ {jfile}: Format differs from SYN_OUT_001.")
            # Let's do a simple key comparison for top-level if it's dict
            all_match = False

if all_match:
    print("\nAll files are in the correct form.")
else:
    print("\nSome files have differences.")
