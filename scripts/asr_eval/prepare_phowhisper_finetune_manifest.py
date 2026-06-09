#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prepare PhoWhisper fine-tuning manifests from selected safe ASR manifests.

Day 2 Week 5 objective:
- Convert selected safe train/dev JSONL manifests into PhoWhisper-ready JSONL.
- Resolve audio paths to absolute paths.
- Preserve transcript text without semantic editing.
- Validate audio existence and transcript availability.
- Enforce train/dev usage guardrails.
- Write skipped rows and summary report.

Output row format:
{
  "sample_id": "...",
  "audio": "/abs/path/to/audio.wav",
  "sentence": "Vietnamese transcript",
  "language": "vi",
  "task": "transcribe",
  "split": "train",
  "source_name": "VietMed",
  "preprocessing_version": "p03_safe_hybrid_v0_1",
  "manual_fallback_applied": false,
  "duration_seconds": 6.2,
  "transcript_chars": 84,
  "transcript_words": 18,
  "train_allowed": true
}

Example:

python scripts/asr_eval/prepare_phowhisper_finetune_manifest.py \
  --input_manifest data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl \
  --output_manifest experiments/asr/finetune/week5/data/train_manifest_for_phowhisper.jsonl \
  --split train \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant" \
  --expected_preprocessing p03_safe_hybrid_v0_1 \
  --fail_on_skipped

python scripts/asr_eval/prepare_phowhisper_finetune_manifest.py \
  --input_manifest data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl \
  --output_manifest experiments/asr/finetune/week5/data/dev_manifest_for_phowhisper.jsonl \
  --split dev \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant" \
  --expected_preprocessing p03_safe_hybrid_v0_1 \
  --fail_on_skipped
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


AUDIO_PATH_KEYS = [
    "preprocessed_audio_path",
    "clean_audio_path",
    "raw_audio_path",
    "audio",
    "audio_path",
]

TRANSCRIPT_KEYS = [
    "transcript_text",
    "reference_text",
    "sentence",
    "text",
    "transcript",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc

            row["_line_no"] = line_no
            rows.append(row)

    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_path(value: str, project_root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return project_root / path


def pick_audio_path(row: dict[str, Any], project_root: Path) -> tuple[Path | None, str | None]:
    for key in AUDIO_PATH_KEYS:
        value = row.get(key)

        if isinstance(value, str) and value.strip():
            return resolve_path(value.strip(), project_root), key

    return None, None


def pick_transcript(row: dict[str, Any]) -> tuple[str | None, str | None]:
    for key in TRANSCRIPT_KEYS:
        value = row.get(key)

        if isinstance(value, str) and value.strip():
            return value, key

    return None, None


def clean_minimal_text(text: str) -> str:
    """
    Minimal cleanup only:
    - strip leading/trailing whitespace
    - collapse repeated whitespace
    No lowercasing.
    No punctuation normalization.
    No Vietnamese text normalization.
    No semantic editing.
    """

    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def word_count_vi(text: str) -> int:
    # Simple whitespace token count. Do not use for WER; only data summary.
    if not text.strip():
        return 0
    return len(text.strip().split())


def try_get_audio_info(audio_path: Path) -> dict[str, Any]:
    """
    Best-effort audio metadata.
    This script can still work if soundfile is not installed,
    but duration validation is better when soundfile exists.
    """

    try:
        import soundfile as sf

        info = sf.info(str(audio_path))

        return {
            "audio_readable": True,
            "sample_rate_hz": int(info.samplerate),
            "channels": int(info.channels),
            "duration_seconds": float(info.duration),
            "frames": int(info.frames),
            "subtype": str(info.subtype),
            "format": str(info.format),
            "audio_error": None,
        }

    except Exception as exc:
        return {
            "audio_readable": False,
            "sample_rate_hz": None,
            "channels": None,
            "duration_seconds": None,
            "frames": None,
            "subtype": None,
            "format": None,
            "audio_error": str(exc),
        }


def get_preprocessing_version(row: dict[str, Any]) -> str | None:
    return (
        row.get("selected_preprocessing_version")
        or row.get("preprocessing_version")
        or row.get("preprocessed_version")
    )


def validate_split_policy(row: dict[str, Any], split: str) -> list[str]:
    issues: list[str] = []

    train_allowed = row.get("train_allowed")

    if split == "train":
        if train_allowed is not True:
            issues.append("train_row_train_allowed_not_true")

    elif split == "dev":
        if train_allowed is True:
            issues.append("dev_row_train_allowed_true")

    else:
        issues.append(f"unsupported_split:{split}")

    return issues


def convert_row(
    row: dict[str, Any],
    split: str,
    project_root: Path,
    expected_preprocessing: str | None,
    require_audio_readable: bool,
    min_duration_seconds: float,
    max_duration_seconds: float | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    sample_id = row.get("sample_id")

    if not sample_id:
        return None, {
            "line_no": row.get("_line_no"),
            "sample_id": None,
            "reason": "missing_sample_id",
            "row": row,
        }

    reasons: list[str] = []

    audio_path, audio_key = pick_audio_path(row, project_root)
    if audio_path is None:
        reasons.append("missing_audio_path")

    transcript, transcript_key = pick_transcript(row)
    if transcript is None:
        reasons.append("missing_transcript")

    preprocessing_version = get_preprocessing_version(row)
    if not preprocessing_version:
        reasons.append("missing_preprocessing_version")

    if expected_preprocessing and preprocessing_version != expected_preprocessing:
        reasons.append(
            f"unexpected_preprocessing_version:{preprocessing_version}:expected:{expected_preprocessing}"
        )

    reasons.extend(validate_split_policy(row, split))

    audio_exists = False
    audio_info: dict[str, Any] = {
        "audio_readable": False,
        "sample_rate_hz": None,
        "channels": None,
        "duration_seconds": None,
        "frames": None,
        "subtype": None,
        "format": None,
        "audio_error": None,
    }

    if audio_path is not None:
        audio_exists = audio_path.exists()

        if not audio_exists:
            reasons.append(f"audio_file_not_found:{audio_path}")
        else:
            audio_info = try_get_audio_info(audio_path)

            if require_audio_readable and not audio_info["audio_readable"]:
                reasons.append(f"audio_not_readable:{audio_info['audio_error']}")

            duration = audio_info.get("duration_seconds")
            if isinstance(duration, (int, float)):
                if duration < min_duration_seconds:
                    reasons.append(f"audio_too_short:{duration:.4f}")

                if max_duration_seconds is not None and duration > max_duration_seconds:
                    reasons.append(f"audio_too_long:{duration:.4f}")

    if transcript is not None:
        sentence = clean_minimal_text(transcript)

        if not sentence:
            reasons.append("empty_transcript_after_minimal_cleanup")
    else:
        sentence = ""

    if reasons:
        return None, {
            "line_no": row.get("_line_no"),
            "sample_id": sample_id,
            "split": split,
            "reasons": reasons,
            "audio_key": audio_key,
            "audio_path": str(audio_path) if audio_path is not None else None,
            "transcript_key": transcript_key,
            "preprocessing_version": preprocessing_version,
            "train_allowed": row.get("train_allowed"),
            "manual_fallback_applied": row.get("manual_fallback_applied"),
            "source_row_preview": {
                k: row.get(k)
                for k in [
                    "sample_id",
                    "source_name",
                    "split_role",
                    "train_allowed",
                    "clean_audio_path",
                    "preprocessed_audio_path",
                    "transcript_text",
                    "reference_text",
                    "preprocessing_version",
                    "selected_preprocessing_version",
                ]
            },
        }

    duration = audio_info.get("duration_seconds")

    converted = {
        "sample_id": sample_id,
        "audio": str(audio_path),
        "sentence": sentence,
        "language": "vi",
        "task": "transcribe",
        "split": split,
        "source_name": row.get("source_name") or row.get("dataset_id") or "VietMed",
        "dataset_id": row.get("dataset_id"),
        "source_type": row.get("source_type"),
        "domain": row.get("domain"),
        "preprocessing_version": preprocessing_version,
        "manual_fallback_applied": bool(row.get("manual_fallback_applied", False)),
        "source_audio_field": audio_key,
        "source_transcript_field": transcript_key,
        "train_allowed": row.get("train_allowed"),
        "split_role": row.get("split_role"),
        "duration_seconds": round(float(duration), 4) if isinstance(duration, (int, float)) else None,
        "sample_rate_hz": audio_info.get("sample_rate_hz"),
        "channels": audio_info.get("channels"),
        "audio_format": audio_info.get("format"),
        "audio_subtype": audio_info.get("subtype"),
        "transcript_chars": len(sentence),
        "transcript_words": word_count_vi(sentence),
        "created_at": now_iso(),
        "created_by": "Duy",
        "manifest_version": "phowhisper_finetune_v0.1.0",
    }

    # Preserve useful traceability fields if available.
    for key in [
        "original_duration_seconds",
        "processed_duration_seconds",
        "duration_delta_seconds",
        "preprocessed_checksum_sha256",
        "source_clean_audio_path",
        "manual_fallback_reason",
        "fallback_from_preprocessing",
    ]:
        if key in row:
            converted[key] = row.get(key)

    return converted, None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None

    values = sorted(values)
    if len(values) == 1:
        return values[0]

    k = (len(values) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)

    if lo == hi:
        return values[int(k)]

    return values[lo] * (hi - k) + values[hi] * (k - lo)


def summarize_manifest(
    input_manifest: Path,
    output_manifest: Path,
    split: str,
    converted: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    expected_preprocessing: str | None,
) -> dict[str, Any]:
    durations = [
        r["duration_seconds"]
        for r in converted
        if isinstance(r.get("duration_seconds"), (int, float))
    ]

    transcript_words = [
        r["transcript_words"]
        for r in converted
        if isinstance(r.get("transcript_words"), (int, float))
    ]

    versions: dict[str, int] = {}
    fallback_count = 0

    for r in converted:
        v = r.get("preprocessing_version") or "unknown"
        versions[v] = versions.get(v, 0) + 1

        if r.get("manual_fallback_applied") is True:
            fallback_count += 1

    skipped_reasons: dict[str, int] = {}
    for s in skipped:
        for reason in s.get("reasons", [s.get("reason", "unknown")]):
            skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1

    p10 = percentile(durations, 0.10)
    p90 = percentile(durations, 0.90)

    summary = {
        "input_manifest": str(input_manifest),
        "output_manifest": str(output_manifest),
        "split": split,
        "expected_preprocessing": expected_preprocessing,
        "n_output_rows": len(converted),
        "n_skipped_rows": len(skipped),
        "preprocessing_versions": versions,
        "manual_fallback_applied_count": fallback_count,
        "duration_seconds": {
            "min": round(min(durations), 4) if durations else None,
            "p10": round(p10, 4) if p10 is not None else None,
            "median": round(statistics.median(durations), 4) if durations else None,
            "mean": round(statistics.mean(durations), 4) if durations else None,
            "p90": round(p90, 4) if p90 is not None else None,
            "max": round(max(durations), 4) if durations else None,
        },
        "transcript_words": {
            "min": min(transcript_words) if transcript_words else None,
            "median": statistics.median(transcript_words) if transcript_words else None,
            "mean": round(statistics.mean(transcript_words), 4) if transcript_words else None,
            "max": max(transcript_words) if transcript_words else None,
        },
        "skipped_reasons": skipped_reasons,
        "created_at": now_iso(),
    }

    return summary


def render_report(summary: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"# Day 2 Week 5 — PhoWhisper Fine-tune Data Preparation: {summary['split']}")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Prepare a PhoWhisper-ready JSONL manifest from the frozen selected safe ASR manifest.")
    lines.append("")
    lines.append("## Input / Output")
    lines.append("")
    lines.append(f"- Input manifest: `{summary['input_manifest']}`")
    lines.append(f"- Output manifest: `{summary['output_manifest']}`")
    lines.append(f"- Split: `{summary['split']}`")
    lines.append(f"- Expected preprocessing: `{summary['expected_preprocessing']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Output rows | {summary['n_output_rows']} |")
    lines.append(f"| Skipped rows | {summary['n_skipped_rows']} |")
    lines.append(f"| Manual fallback applied | {summary['manual_fallback_applied_count']} |")
    lines.append("")
    lines.append("## Preprocessing versions")
    lines.append("")
    lines.append("| Version | Count |")
    lines.append("|---|---:|")

    for version, count in summary["preprocessing_versions"].items():
        lines.append(f"| `{version}` | {count} |")

    lines.append("")
    lines.append("## Duration summary")
    lines.append("")
    lines.append("| Metric | Seconds |")
    lines.append("|---|---:|")

    for key, value in summary["duration_seconds"].items():
        lines.append(f"| {key} | {value} |")

    lines.append("")
    lines.append("## Transcript word count")
    lines.append("")
    lines.append("| Metric | Words |")
    lines.append("|---|---:|")

    for key, value in summary["transcript_words"].items():
        lines.append(f"| {key} | {value} |")

    lines.append("")
    lines.append("## Skipped reasons")
    lines.append("")

    if summary["skipped_reasons"]:
        lines.append("| Reason | Count |")
        lines.append("|---|---:|")
        for reason, count in summary["skipped_reasons"].items():
            lines.append(f"| `{reason}` | {count} |")
    else:
        lines.append("No skipped rows.")

    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- Transcript text was minimally whitespace-cleaned only.")
    lines.append("- No semantic transcript editing was performed.")
    lines.append("- test_holdout was not used.")
    lines.append("- The output uses absolute local audio paths for HuggingFace loading.")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input_manifest",
        required=True,
        help="Selected safe ASR manifest JSONL.",
    )

    parser.add_argument(
        "--output_manifest",
        required=True,
        help="PhoWhisper fine-tune manifest JSONL.",
    )

    parser.add_argument(
        "--split",
        required=True,
        choices=["train", "dev"],
    )

    parser.add_argument(
        "--project_root",
        default=str(PROJECT_ROOT_DEFAULT),
    )

    parser.add_argument(
        "--expected_preprocessing",
        default="p03_safe_hybrid_v0_1",
    )

    parser.add_argument(
        "--require_audio_readable",
        action="store_true",
        help="Require soundfile-readable audio. Recommended.",
    )

    parser.add_argument(
        "--min_duration_seconds",
        type=float,
        default=0.3,
    )

    parser.add_argument(
        "--max_duration_seconds",
        type=float,
        default=None,
    )

    parser.add_argument(
        "--fail_on_skipped",
        action="store_true",
        help="Exit with error if any row is skipped.",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)

    input_manifest = Path(args.input_manifest)
    if not input_manifest.is_absolute():
        input_manifest = project_root / input_manifest

    output_manifest = Path(args.output_manifest)
    if not output_manifest.is_absolute():
        output_manifest = project_root / output_manifest

    if not input_manifest.exists():
        raise FileNotFoundError(f"Input manifest not found: {input_manifest}")

    rows = read_jsonl(input_manifest)

    converted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for row in rows:
        out, skip = convert_row(
            row=row,
            split=args.split,
            project_root=project_root,
            expected_preprocessing=args.expected_preprocessing,
            require_audio_readable=args.require_audio_readable,
            min_duration_seconds=args.min_duration_seconds,
            max_duration_seconds=args.max_duration_seconds,
        )

        if out is not None:
            converted.append(out)

        if skip is not None:
            skipped.append(skip)

    write_jsonl(output_manifest, converted)

    skipped_path = output_manifest.with_name(output_manifest.stem + "_skipped.jsonl")
    summary_path = output_manifest.with_name(output_manifest.stem + "_summary.json")
    report_path = output_manifest.with_name(output_manifest.stem + "_REPORT.md")

    write_jsonl(skipped_path, skipped)

    summary = summarize_manifest(
        input_manifest=input_manifest,
        output_manifest=output_manifest,
        split=args.split,
        converted=converted,
        skipped=skipped,
        expected_preprocessing=args.expected_preprocessing,
    )

    write_json(summary_path, summary)
    report_path.write_text(render_report(summary), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[DONE] output_manifest: {output_manifest}")
    print(f"[DONE] skipped_rows:    {skipped_path}")
    print(f"[DONE] summary:         {summary_path}")
    print(f"[DONE] report:          {report_path}")

    if skipped and args.fail_on_skipped:
        raise SystemExit(f"Skipped rows found: {len(skipped)}")


if __name__ == "__main__":
    main()