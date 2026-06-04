import os
import json
from datetime import datetime

base_dir = '/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/synthetic_data/outpatient_v0_1'
folders_to_process = ['SYN_OUT_002', 'SYN_OUT_003', 'SYN_OUT_004', 'SYN_OUT_005', 'SYN_OUT_006']

for folder in folders_to_process:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        continue
    
    encounter_id = folder

    # 1. Transcript segments
    transcript_path = os.path.join(folder_path, 'transcript_segments_gold.json')
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        new_transcript_data = []
        for item in transcript_data:
            speaker_str = item.get('speaker', 'speaker_0')
            speaker_role = 'doctor' if '0' in speaker_str else 'patient'
            speaker_id = 'Speaker_0' if '0' in speaker_str else 'Speaker_1'
            new_item = {
                "segment_id": item.get('segment_id', f"seg_{len(new_transcript_data)+1:03d}"),
                "encounter_id": encounter_id,
                "start_time": item.get('start_time', 0.0),
                "end_time": item.get('end_time', 0.0),
                "speaker_id": speaker_id,
                "speaker_role": speaker_role,
                "text": item.get('text', ''),
                "confidence": 1.0,
                "audio_span": {
                    "start_time": item.get('start_time', 0.0),
                    "end_time": item.get('end_time', 0.0)
                },
                "created_at": "2026-06-03T00:00:00+07:00",
                "version": "v0.1.0"
            }
            new_transcript_data.append(new_item)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(new_transcript_data, f, ensure_ascii=False, indent=4)

    # 2. Metadata
    metadata_path = os.path.join(folder_path, 'encounter_metadata.json')
    new_meta = {
        "encounter_id": encounter_id,
        "dataset_id": "A_SYNTHETIC_VI_OUTPATIENT_ENCOUNTERS",
        "source_type": "synthetic",
        "setting": "outpatient",
        "specialty": "internal_medicine",
        "language": "vi-VN",
        "audio_path": "not_applicable",
        "transcript_path": "transcript_segments_gold.json",
        "contains_phi": "no",
        "consent_status": "synthetic",
        "license_status": "internal",
        "allowed_use": ["training", "evaluation", "demo"],
        "review_status": "gold",
        "version": "v0.1",
        "created_at": "2026-06-03T00:00:00Z",
        "updated_at": "2026-06-03T00:00:00Z",
        "governance_status": "approved_internal",
        "created_by": "Duy",
        "retention_policy": "keep_versioned",
        "access_control_policy": "project_team",
        "audit_log_required": False,
        "provenance": {
            "recording_environment": "simulated",
            "collection_method": "script_generated",
            "deidentification_status": "not_required_synthetic"
        },
        "clinical_note": {
            "note_format": "soap",
            "reviewed_note_path": "soap_note_gold.md",
            "doctor_confirmation_status": "accepted",
            "reviewed_by": "synthetic_reviewer",
            "reviewed_at": "2026-06-03T00:00:00Z"
        }
    }
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(new_meta, f, ensure_ascii=False, indent=4)

    # 3. Clinical Facts
    for fact_file in ['clinical_facts_gold.json', 'clinical_facts_candidate.json']:
        fact_path = os.path.join(folder_path, fact_file)
        if os.path.exists(fact_path):
            with open(fact_path, 'r', encoding='utf-8') as f:
                facts = json.load(f)
            new_facts = []
            for idx, item in enumerate(facts):
                fact_id = item.get('fact_id', f"fact_{idx+1:03d}")
                
                orig_text = ""
                evidences = item.get('evidence', item.get('source_evidence', []))
                if evidences and isinstance(evidences, list) and len(evidences) > 0:
                    orig_text = evidences[0].get('quote', evidences[0].get('text', ''))
                if not orig_text:
                    orig_text = item.get('original_text', item.get('normalized_text', ''))

                new_item = {
                    "fact_id": fact_id,
                    "encounter_id": encounter_id,
                    "fact_type": item.get('category', item.get('fact_type', 'symptom')),
                    "original_text": orig_text,
                    "normalized_text": item.get('normalized_text', ''),
                    "assertion": item.get('status', item.get('assertion', 'present')),
                    "speaker_role": "patient",
                    "clinical_subject": {
                        "subject_type": "patient",
                        "relationship_to_patient": "self"
                    },
                    "source_segment_ids": [ev.get('segment_id', '') for ev in evidences],
                    "source_evidence": evidences,
                    "doctor_confirmation_status": "accepted",
                    "coding_candidates": item.get('coding_candidates', []),
                    "reviewed_by": "synthetic_reviewer",
                    "reviewed_at": "2026-06-03T00:00:00+07:00",
                    "review_status": "gold",
                    "confidence": 1.0,
                    "created_at": "2026-06-03T00:00:00+07:00",
                    "created_by": "Duy",
                    "version": "v0.1.0"
                }
                new_facts.append(new_item)
            with open(fact_path, 'w', encoding='utf-8') as f:
                json.dump(new_facts, f, ensure_ascii=False, indent=4)

    # 4. Encounter Outcome
    outcome_path = os.path.join(folder_path, 'encounter_outcome.json')
    if os.path.exists(outcome_path):
        with open(outcome_path, 'r', encoding='utf-8') as f:
            outcome = json.load(f)
        
        red_flags = []
        for rf in outcome.get('red_flags_to_watch', []):
            flag_text = ""
            if isinstance(rf, str):
                flag_text = rf
            elif isinstance(rf, dict):
                flag_text = rf.get('symptom', rf.get('red_flag_text', ''))
            red_flags.append({
                "red_flag_text": flag_text,
                "review_status": "pending_review"
            })
            
        prim_ass = outcome.get('primary_assessment', {})
        if isinstance(prim_ass, dict):
            prim_desc = prim_ass.get('condition', prim_ass.get('description', ''))
        else:
            prim_desc = str(prim_ass)
            
        disposition = outcome.get('disposition', {})
        timeframe = "3-5 ngày"
        if isinstance(disposition, dict):
            timeframe = str(disposition.get('follow_up_days', '3-5 ngày'))
        elif isinstance(outcome.get('follow_up_timeframe'), str):
            timeframe = outcome.get('follow_up_timeframe')
            
        new_outcome = {
            "schema_version": "2020-12",
            "outcome_id": f"OUT_{encounter_id}",
            "encounter_id": encounter_id,
            "primary_assessment": prim_desc,
            "secondary_assessments": [],
            "recommended_action": "Theo dõi và điều trị triệu chứng",
            "follow_up_required": True,
            "follow_up_timeframe": timeframe,
            "red_flags_to_watch": red_flags,
            "disposition": "outpatient_follow_up",
            "source_segment_ids": [],
            "doctor_confirmation_status": "pending",
            "review_status": "pending_review",
            "safety_critical": False,
            "created_at": "2026-06-03T00:00:00+07:00",
            "created_by": "Duy",
            "version": "v0.1.0"
        }
        with open(outcome_path, 'w', encoding='utf-8') as f:
            json.dump(new_outcome, f, ensure_ascii=False, indent=4)

    # 5. SOAP Evidence
    soap_ev_path = os.path.join(folder_path, 'soap_source_evidence.json')
    if os.path.exists(soap_ev_path):
        with open(soap_ev_path, 'r', encoding='utf-8') as f:
            soap_ev = json.load(f)
        
        new_claims = []
        if isinstance(soap_ev, list):
            claims_to_process = soap_ev
        else:
            claims_to_process = soap_ev.get('claims', [])
            
        for claim in claims_to_process:
            evidences = claim.get('source_evidence', [])
            new_claim = {
                "claim_id": claim.get('claim_id', f"claim_{len(new_claims)+1:03d}"),
                "section": claim.get('section', 'S'),
                "claim_text": claim.get('summary', claim.get('claim_text', '')),
                "claim_type": claim.get('claim_type', 'subjective_history'),
                "source_segment_ids": [ev.get('segment_id', '') for ev in evidences],
                "source_evidence": evidences,
                "evidence_status": "supported",
                "verification_status": "verified",
                "risk_if_wrong": "moderate",
                "requires_doctor_confirmation": False
            }
            new_claims.append(new_claim)
            
        new_soap = {
            "schema_version": "2020-12",
            "encounter_id": encounter_id,
            "note_id": f"note_{encounter_id[-3:]}",
            "note_format": "soap_lite",
            "overall_verification_status": "verified",
            "unsupported_claim_count": 0,
            "contradicted_claim_count": 0,
            "created_at": "2026-06-03T00:00:00+07:00",
            "created_by": "Duy",
            "version": "v0.1.0",
            "claims": new_claims
        }
        with open(soap_ev_path, 'w', encoding='utf-8') as f:
            json.dump(new_soap, f, ensure_ascii=False, indent=4)

    # 6. Add annotation_notes.md
    note_path = os.path.join(folder_path, 'annotation_notes.md')
    if not os.path.exists(note_path):
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write("# Ghi chú của Reviewer\n\n- Dữ liệu đã được chuẩn hóa theo định dạng Gold Standard.")

    # 7. Add script.md
    script_path = os.path.join(folder_path, 'script.md')
    if not os.path.exists(script_path):
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("# Kịch bản hội thoại\n\n(Chưa có nội dung)")
