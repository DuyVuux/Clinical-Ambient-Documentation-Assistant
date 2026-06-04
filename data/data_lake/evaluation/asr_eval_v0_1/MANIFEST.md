# ASR Evaluation Manifest v0.1

## Purpose

Fixed ASR benchmark for evaluating models against the WER < 20% target.

## Main target

VietMed medical speech holdout.

## Rules

- This set is holdout only.
- Do not train on this set.
- Do not use this set for checkpoint selection.
- Do not edit transcripts after seeing model output.
- Report strict WER and normalized WER.

## Files

- vietmed_test_holdout_v0_1.jsonl
- vietmed_dev_v0_1.jsonl
- vietmed_train_candidate_v0_1.jsonl

## Current baseline

- Boss baseline: Whisper small trained/fine-tuned on VietMed, WER ~31%.

## Split quality

| Field | Value |
|---|---|
| total_vietmed_samples | TBD |
| train_candidate | TBD |
| dev | TBD |
| test_holdout | TBD |
| split_mode | debug_only / small_benchmark / proper_benchmark |

## Reporting rule

If split_mode = debug_only:
- WER is only for pipeline debugging.
- Do not report as final benchmark.

If split_mode = small_benchmark:
- WER can be used for early comparison.
- Do not claim final target achieved.

If split_mode = proper_benchmark:
- WER can be used for model comparison and mentor report.