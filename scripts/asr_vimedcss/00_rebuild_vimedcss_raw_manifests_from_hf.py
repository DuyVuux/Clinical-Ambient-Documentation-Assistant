#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rebuild ViMedCSS raw manifests directly from HuggingFace dataset.

Why this script exists:
- Existing raw manifests may be incomplete, dummy, or schema-corrupted.
- Week 6 ViMedCSS track requires true raw manifests with:
  - audio
  - segment_text
  - duration_seconds
  - official splits: train/validation/test/hard

This script should be run on Colab CPU, not local laptop.

It does NOT download full audio arrays if Audio(decode=False) works.
It writes lightweight JSONL manifests for later audit/subset materialization.

Example:

python scripts/vimedcss/00_rebuild_vimedcss_raw_manifests_from_hf.py \
  --dataset_id tensorxt/ViMedCSS \
  --vimedcss_root /content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss \
  --cache_dir /content/vimedcss_work/hf_cache \
  --splits train validation test hard \
  --overwrite
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets import Audio, load_dataset


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip())
    return re.sub(r"\s+", " ", str(value).strip())


def get_first_present(row: dict[str, Any], keys: list[str]) -> tuple[Any, str | None]:
    for key in keys:
        if key in row and row[key] not in [None, ""]:
            return row[key], key
    return None, None


def extract_audio_metadata(audio_value: Any) -> dict[str, Any]:
    """
    Avoid writing audio arrays or bytes into manifest.

    With datasets.Audio(decode=False), audio usually becomes:
    {
      "path": "...",
      "bytes": None or b"..."
    }

    We keep path and whether bytes exist, but never serialize raw bytes.
    """

    out = {
        "audio_path": None,
        "audio_bytes_present": False,
        "audio_type": type(audio_value).__name__,
    }

    if isinstance(audio_value, dict):
        path = (
            audio_value.get("path")
            or audio_value.get("filename")
            or audio_value.get("file")
        )

        out["audio_path"] = path
        out["audio_bytes_present"] = audio_value.get("bytes") is not None

    elif isinstance(audio_value, str):
        out["audio_path"] = audio_value

    else:
        out["audio_path"] = None

    return out


def list_columns(dataset) -> list[str]:
    features = getattr(dataset, "features", None)
    if features is not None:
        try:
            return list(features.keys())
        except Exception:
            pass

    # Fallback: materialize one row.
    first = next(iter(dataset))
    return list(first.keys())


def infer_columns(columns: list[str]) -> dict[str, str | None]:
    audio_candidates = [
        "audio",
        "audio_path",
        "path",
        "wav",
        "wav_path",
        "file",
    ]

    text_candidates = [
        "segment_text",
        "text",
        "transcript",
        "transcript_text",
        "sentence",
    ]

    duration_candidates = [
        "duration_seconds",
        "duration",
        "audio_duration",
    ]

    id_candidates = [
        "segment_id",
        "sample_id",
        "id",
        "utt_id",
    ]

    def pick(candidates: list[str]) -> str | None:
        for c in candidates:
            if c in columns:
                return c
        return None

    return {
        "audio_col": pick(audio_candidates),
        "text_col": pick(text_candidates),
        "duration_col": pick(duration_candidates),
        "id_col": pick(id_candidates),
    }


def maybe_cast_audio_decode_false(dataset, audio_col: str | None):
    if audio_col is None:
        return dataset

    try:
        return dataset.cast_column(audio_col, Audio(decode=False))
    except Exception as exc:
        print(f"[WARN] Could not cast {audio_col} to Audio(decode=False): {exc}")
        return dataset


def normalize_cs_terms(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [safe_text(x) for x in value if safe_text(x)]

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []

        # Try JSON-like list first.
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [safe_text(x) for x in parsed if safe_text(x)]
        except Exception:
            pass

        # Fallback comma/semicolon split.
        parts = re.split(r"[,;|]", value)
        return [safe_text(x) for x in parts if safe_text(x)]

    return [safe_text(value)]


def build_manifest_for_split(
    dataset_id: str,
    split: str,
    output_path: Path,
    cache_dir: str | None,
    streaming: bool,
    max_rows: int | None,
) -> dict[str, Any]:
    print(f"[INFO] Loading dataset split={split}, streaming={streaming}")

    ds_for_columns = load_dataset(
        dataset_id,
        split=split,
        streaming=streaming,
        cache_dir=cache_dir,
    )

    columns = list_columns(ds_for_columns)
    inferred = infer_columns(columns)

    print(f"[INFO] split={split} columns={columns}")
    print(f"[INFO] split={split} inferred={inferred}")

    if inferred["audio_col"] is None:
        raise ValueError(f"Could not infer audio column for split={split}. Columns={columns}")

    if inferred["text_col"] is None:
        raise ValueError(f"Could not infer text column for split={split}. Columns={columns}")

    # Reload to avoid consuming iterable after peeking.
    ds = load_dataset(
        dataset_id,
        split=split,
        streaming=streaming,
        cache_dir=cache_dir,
    )

    ds = maybe_cast_audio_decode_false(ds, inferred["audio_col"])

    rows: list[dict[str, Any]] = []

    missing_audio = 0
    missing_text = 0
    missing_duration = 0

    for idx, item in enumerate(ds):
        if max_rows is not None and idx >= max_rows:
            break

        audio_value = item.get(inferred["audio_col"])
        audio_meta = extract_audio_metadata(audio_value)

        text_value = safe_text(item.get(inferred["text_col"]))

        duration_value = None
        if inferred["duration_col"] is not None:
            duration_value = item.get(inferred["duration_col"])

        segment_id_value = None
        if inferred["id_col"] is not None:
            segment_id_value = item.get(inferred["id_col"])

        if segment_id_value in [None, ""]:
            segment_id_value = f"vimedcss_{split}_{idx:06d}"

        cs_terms_raw = item.get("cs_terms_list")
        cs_terms_list = normalize_cs_terms(cs_terms_raw)

        cs_terms_count = item.get("cs_terms_count")
        if cs_terms_count in [None, ""]:
            cs_terms_count = len(cs_terms_list)

        row = {
            "sample_id": f"vimedcss_{split}_{idx:06d}",
            "segment_id": safe_text(segment_id_value),
            "dataset_id": dataset_id,
            "split": split,
            "row_index": idx,

            # Canonical ViMedCSS columns expected by Week 6.
            "audio": audio_meta["audio_path"],
            "audio_path": audio_meta["audio_path"],
            "segment_text": text_value,
            "duration_seconds": duration_value,

            # Metadata.
            "sampling_rate": item.get("sampling_rate"),
            "cs_terms_list": cs_terms_list,
            "cs_terms_count": cs_terms_count,
            "topic": item.get("topic"),
            "original_video_link": item.get("original_video_link"),
            "original_video_title": item.get("original_video_title"),
            "start_time": item.get("start_time"),
            "end_time": item.get("end_time"),

            # Traceability.
            "_source_audio_col": inferred["audio_col"],
            "_source_text_col": inferred["text_col"],
            "_source_duration_col": inferred["duration_col"],
            "_source_id_col": inferred["id_col"],
            "_audio_type": audio_meta["audio_type"],
            "_audio_bytes_present": audio_meta["audio_bytes_present"],
            "_created_at": now_iso(),
        }

        if not row["audio"]:
            missing_audio += 1
        if not row["segment_text"]:
            missing_text += 1
        if row["duration_seconds"] in [None, ""]:
            missing_duration += 1

        rows.append(row)

    write_jsonl(output_path, rows)

    summary = {
        "dataset_id": dataset_id,
        "split": split,
        "output_path": str(output_path),
        "rows": len(rows),
        "columns": columns,
        "inferred": inferred,
        "missing_audio": missing_audio,
        "missing_segment_text": missing_text,
        "missing_duration_seconds": missing_duration,
        "max_rows": max_rows,
        "streaming": streaming,
        "created_at": now_iso(),
    }

    return summary


def render_report(summaries: list[dict[str, Any]]) -> str:
    lines: list[str] = []

    lines.append("# ViMedCSS Raw Manifest Rebuild Report")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Rebuild raw manifests directly from HuggingFace `tensorxt/ViMedCSS` because previous local raw manifests were incomplete or dummy.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Split | Rows | Missing audio | Missing segment_text | Missing duration | Audio col | Text col | Output |")
    lines.append("|---|---:|---:|---:|---:|---|---|---|")

    for s in summaries:
        lines.append(
            f"| {s['split']} | {s['rows']} | {s['missing_audio']} | "
            f"{s['missing_segment_text']} | {s['missing_duration_seconds']} | "
            f"`{s['inferred']['audio_col']}` | `{s['inferred']['text_col']}` | "
            f"`{s['output_path']}` |"
        )

    lines.append("")
    lines.append("## Decision")
    lines.append("")
    if all(s["missing_segment_text"] == 0 for s in summaries):
        lines.append("Raw manifests are usable for Phase 1 sample-based audit.")
    else:
        lines.append("Some manifests still have missing `segment_text`; inspect dataset schema before continuing.")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset_id", default="tensorxt/ViMedCSS")
    parser.add_argument("--vimedcss_root", required=True)
    parser.add_argument("--cache_dir", default="/content/vimedcss_work/hf_cache")
    parser.add_argument("--splits", nargs="+", default=["train", "validation", "test", "hard"])
    parser.add_argument("--max_rows", type=int, default=None)
    parser.add_argument("--no_streaming", action="store_true")
    parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()

    vimedcss_root = Path(args.vimedcss_root)
    output_dir = vimedcss_root / "manifests" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    Path(args.cache_dir).mkdir(parents=True, exist_ok=True)

    summaries = []

    for split in args.splits:
        output_path = output_dir / f"vimedcss_{split}_raw.jsonl"

        if output_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"Output exists: {output_path}. Use --overwrite to replace."
            )

        summary = build_manifest_for_split(
            dataset_id=args.dataset_id,
            split=split,
            output_path=output_path,
            cache_dir=args.cache_dir,
            streaming=not args.no_streaming,
            max_rows=args.max_rows,
        )

        summaries.append(summary)

    report_dir = vimedcss_root / "data_audit"
    report_dir.mkdir(parents=True, exist_ok=True)

    write_json(report_dir / "REBUILD_VIMEDCSS_RAW_MANIFESTS_SUMMARY.json", summaries)
    (report_dir / "REBUILD_VIMEDCSS_RAW_MANIFESTS_REPORT.md").write_text(
        render_report(summaries),
        encoding="utf-8",
    )

    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    print("[DONE] Raw manifests rebuilt.")


if __name__ == "__main__":
    main()