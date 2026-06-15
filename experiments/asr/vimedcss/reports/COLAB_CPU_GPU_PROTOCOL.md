# Colab CPU/GPU Protocol for ViMedCSS

## Principle

Local laptop coordinates the experiment. Google Drive stores heavy artifacts. Colab CPU prepares data. Colab GPU trains/evaluates.

## Local laptop

Allowed:

- write code
- manage repo
- keep small manifests/reports
- inspect JSONL/CSV metadata

Not allowed:

- download full ViMedCSS
- train PhoWhisper-medium
- store multiple large checkpoints
- let Hugging Face cache fill `/home`

## Google Drive

Use Drive as persistent storage for:

- subset archives
- predictions
- metrics
- reports
- best checkpoints
- final models

## Colab CPU

Use CPU runtime for:

- dataset streaming
- schema verification
- manifest creation
- sample-based audit
- subset materialization
- `.tar.gz` archive creation

Do not enable T4 just to download data.

## Colab GPU/T4

Use GPU runtime only for:

- baseline ASR
- fine-tuning
- evaluation
- forgetting check

## Correct archive flow

```text
Drive archive
→ copy to /content
→ extract in /content
→ train/eval from /content
→ copy predictions/metrics/checkpoints back to Drive
```

## Cache policy

Recommended Colab cache:

```text
/content/vimedcss_work/hf_cache
/content/vimedcss_work/datasets_cache
/content/vimedcss_work/runs
```
