import os
import json

base_dir = '/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/synthetic_data/outpatient_v0_1'
folders = [f'SYN_OUT_{str(i).zfill(3)}' for i in range(1, 11)]

expected_files = {
    'annotation_notes.md',
    'clinical_facts_candidate.json',
    'clinical_facts_gold.json',
    'encounter_metadata.json',
    'encounter_outcome.json',
    'script.md',
    'soap_note_gold.md',
    'soap_source_evidence.json',
    'transcript_segments_gold.json'
}

issues = []

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        issues.append(f"[{folder}] Missing directory")
        continue

    # Check files existence
    files_in_folder = set(os.listdir(folder_path))
    missing_files = expected_files - files_in_folder
    if missing_files:
        issues.append(f"[{folder}] Missing files: {', '.join(missing_files)}")
        
    extra_files = files_in_folder - expected_files
    # Only report extra JSON/MD files
    extra_files = {f for f in extra_files if f.endswith('.json') or f.endswith('.md')}
    if extra_files:
        issues.append(f"[{folder}] Extra files: {', '.join(extra_files)}")

    # Helper to load JSON
    def load_json(filename):
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except Exception as e:
                    issues.append(f"[{folder}] {filename} is invalid JSON: {e}")
        return None

    # Check encounter_metadata
    meta = load_json('encounter_metadata.json')
    if meta:
        if meta.get('encounter_id') != folder:
            issues.append(f"[{folder}] encounter_metadata.json has wrong encounter_id: {meta.get('encounter_id')}")

    # Check transcript
    transcripts = load_json('transcript_segments_gold.json')
    if transcripts:
        for t in transcripts:
            if not t.get('segment_id'):
                issues.append(f"[{folder}] transcript missing segment_id")
            if t.get('encounter_id') != folder:
                issues.append(f"[{folder}] transcript {t.get('segment_id')} has wrong encounter_id")

    # Check clinical facts
    for ftype in ['clinical_facts_gold.json', 'clinical_facts_candidate.json']:
        facts = load_json(ftype)
        if facts:
            for fact in facts:
                if not fact.get('fact_id'):
                    issues.append(f"[{folder}] {ftype} missing fact_id")
                if fact.get('encounter_id') != folder:
                    issues.append(f"[{folder}] {ftype} {fact.get('fact_id')} has wrong encounter_id")
                if not isinstance(fact.get('source_segment_ids'), list):
                    issues.append(f"[{folder}] {ftype} {fact.get('fact_id')} source_segment_ids is not a list")

    # Check outcome
    outcome = load_json('encounter_outcome.json')
    if outcome:
        if outcome.get('encounter_id') != folder:
            issues.append(f"[{folder}] encounter_outcome.json has wrong encounter_id")
        if not isinstance(outcome.get('primary_assessment'), str):
            issues.append(f"[{folder}] encounter_outcome.json primary_assessment is not a string")
        if not isinstance(outcome.get('source_segment_ids'), list):
            issues.append(f"[{folder}] encounter_outcome.json source_segment_ids is not a list")
            
    # Check soap evidence
    soap = load_json('soap_source_evidence.json')
    if soap:
        if soap.get('encounter_id') != folder:
            issues.append(f"[{folder}] soap_source_evidence.json has wrong encounter_id")
        for claim in soap.get('claims', []):
            if not claim.get('claim_id'):
                issues.append(f"[{folder}] soap claim missing claim_id")
            if not isinstance(claim.get('source_segment_ids'), list):
                issues.append(f"[{folder}] soap claim {claim.get('claim_id')} source_segment_ids is not a list")

if not issues:
    print("ALL CLEAR: Tất cả các file trong 10 thư mục đều tuân thủ cấu trúc chuẩn, không tìm thấy lỗi.")
else:
    print("TÌM THẤY LỖI:")
    for issue in issues:
        print(" -", issue)
