import os
import json

base_dir = '/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/synthetic_data/outpatient_v0_1'
folders_to_process = [f'SYN_OUT_{str(i).zfill(3)}' for i in range(2, 11)]

for folder in folders_to_process:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        continue

    outcome_path = os.path.join(folder_path, 'encounter_outcome.json')
    facts_path = os.path.join(folder_path, 'clinical_facts_gold.json')

    if os.path.exists(outcome_path) and os.path.exists(facts_path):
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts = json.load(f)
            
        segment_ids = set()
        for fact in facts:
            for seg_id in fact.get('source_segment_ids', []):
                segment_ids.add(seg_id)
                
        # Sort segment ids correctly (e.g. seg_001, seg_002)
        sorted_segment_ids = sorted(list(segment_ids))

        with open(outcome_path, 'r', encoding='utf-8') as f:
            outcome = json.load(f)
            
        outcome['source_segment_ids'] = sorted_segment_ids
        
        with open(outcome_path, 'w', encoding='utf-8') as f:
            json.dump(outcome, f, ensure_ascii=False, indent=4)
            
print("Đã hoàn tất việc trích xuất và điền source_segment_ids!")
