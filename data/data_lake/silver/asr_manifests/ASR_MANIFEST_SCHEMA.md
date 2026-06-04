# ASR Manifest Schema v0.1

Mỗi dòng JSONL là một audio sample dùng cho ASR.

## Required fields

- sample_id
- dataset_id
- source_name
- source_type
- split_role
- raw_audio_path
- raw_transcript_path
- clean_audio_path
- transcript_text
- language
- duration_seconds
- sample_rate_hz
- checksum_sha256
- license_status
- allowed_use
- governance_status
- wer_eval_allowed
- train_allowed
- created_at
- version

## split_role

- smoke_test
- train_candidate
- dev_candidate
- test_holdout
- reference_only

## Rule

Nếu license_status != clear/internal thì train_allowed = false.
Nếu split_role = test_holdout thì train_allowed = false.