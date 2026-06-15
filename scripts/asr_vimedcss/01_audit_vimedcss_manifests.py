#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 1 — ViMedCSS sample-based manifest audit.

This script audits existing ViMedCSS raw JSONL manifests before subset
engineering and progressive fine-tuning.

It does NOT:
- download the full dataset
- materialize audio
- train a model
- modify manifests
- change official splits

Expected input manifests:

Preferred:
  experiments/asr/vimedcss/manifests/raw/vimedcss_train_raw.jsonl
  experiments/asr/vimedcss/manifests/raw/vimedcss_validation_raw.jsonl
  experiments/asr/vimedcss/manifests/raw/vimedcss_test_raw.jsonl
  experiments/asr/vimedcss/manifests/raw/vimedcss_hard_raw.jsonl

Fallback:
  experiments/asr/vimedcss/manifests/vimedcss_train_raw.jsonl
  experiments/asr/vimedcss/manifests/vimedcss_validation_raw.jsonl
  experiments/asr/vimedcss/manifests/vimedcss_test_raw.jsonl
  experiments/asr/vimedcss/manifests/vimedcss_hard_raw.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SPLITS = ["train", "validation", "test", "hard"]

EXPECTED_FIELDS = [
    "segment_id",
    "audio",
    "duration_seconds",
    "segment_text",
    "cs_terms_list",
    "cs_terms_count",
    "topic",
    "original_video_link",
    "original_video_title",
    "start_time",
    "end_time",
]

EN_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+\-/.]*")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")
WHITESPACE_RE = re.compile(r"\s+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return float(value)
    if isinstance(value, str):
        v = value.strip().replace(",", ".")
        if not v:
            return None
        try:
            out = float(v)
            if math.isnan(out) or math.isinf(out):
                return None
            return out
        except ValueError:
            return None
    return None


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return int(value)
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        try:
            return int(float(v))
        except ValueError:
            return None
    return None


def parse_time_to_seconds(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return float(value)
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        if ":" in v:
            parts = v.split(":")
            try:
                if len(parts) == 2:
                    return int(parts[0]) * 60 + float(parts[1])
                if len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            except (ValueError, IndexError):
                pass
        return safe_float(v)
    return None


def normalize_text_minimal(text: Any) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    text = WHITESPACE_RE.sub(" ", text)
    return text


def count_words(text: str) -> int:
    text = text.strip()
    if not text:
        return 0
    return len(text.split())


def count_english_tokens(text: str) -> int:
    return len(EN_TOKEN_RE.findall(text))


def count_numbers(text: str) -> int:
    return len(NUMBER_RE.findall(text))


def parse_cs_terms(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    if isinstance(value, str):
        v = value.strip()
        if not v:
            return []

        try:
            decoded = json.loads(v)
            if isinstance(decoded, list):
                return [str(x).strip() for x in decoded if str(x).strip()]
        except Exception:
            pass

        parts = re.split(r"[,;|]", v)
        return [p.strip() for p in parts if p.strip()]

    return [str(value).strip()] if str(value).strip() else []


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


def describe_numeric(values: list[float]) -> dict[str, Any]:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "max": None,
        }

    return {
        "count": len(clean),
        "min": round(min(clean), 4),
        "p10": round(percentile(clean, 0.10), 4),
        "median": round(statistics.median(clean), 4),
        "mean": round(statistics.mean(clean), 4),
        "p90": round(percentile(clean, 0.90), 4),
        "max": round(max(clean), 4),
    }


def detect_manifest_path(vimedcss_root: Path, split: str) -> Path:
    preferred = vimedcss_root / "manifests" / "raw" / f"vimedcss_{split}_raw.jsonl"
    legacy = vimedcss_root / "manifests" / f"vimedcss_{split}_raw.jsonl"

    if preferred.exists():
        return preferred
    return legacy


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                row = {
                    "_invalid_json": True,
                    "_raw_line": line[:500],
                }
            row["_line_no"] = line_no
            rows.append(row)

    return rows


def has_audio_value(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, dict):
        if value.get("path") or value.get("bytes"):
            return True
        return bool(value)

    if isinstance(value, str):
        return bool(value.strip())

    return True


def build_sample_audit(row: dict[str, Any], split: str) -> dict[str, Any]:
    segment_id = row.get("segment_id") or row.get("sample_id") or f"{split}_line_{row.get('_line_no')}"

    text = normalize_text_minimal(row.get("segment_text"))
    duration = safe_float(row.get("duration_seconds"))
    start_time = parse_time_to_seconds(row.get("start_time"))
    end_time = parse_time_to_seconds(row.get("end_time"))

    word_count = count_words(text)
    text_len = len(text)
    english_token_count = count_english_tokens(text)
    number_count = count_numbers(text)

    cs_terms = parse_cs_terms(row.get("cs_terms_list"))
    cs_terms_count_given = safe_int(row.get("cs_terms_count"))
    cs_terms_count = cs_terms_count_given if cs_terms_count_given is not None else len(cs_terms)

    topic = normalize_text_minimal(row.get("topic")) or "unknown"
    audio_present = has_audio_value(row.get("audio"))

    suspect_reasons: list[str] = []
    info_flags: list[str] = []

    if row.get("_invalid_json"):
        suspect_reasons.append("invalid_json")

    if not audio_present:
        suspect_reasons.append("missing_audio")

    if duration is None:
        suspect_reasons.append("missing_duration")
    else:
        if duration < 1.0:
            suspect_reasons.append("duration_too_short_lt_1s")
        if duration > 25.0:
            suspect_reasons.append("duration_too_long_gt_25s")

    if not text:
        suspect_reasons.append("missing_segment_text")
    else:
        if text_len <= 3:
            suspect_reasons.append("text_too_short_len_le_3")
        if word_count <= 1:
            suspect_reasons.append("too_few_words_le_1")

    if cs_terms_count_given is None and row.get("cs_terms_count") is not None:
        suspect_reasons.append("cs_terms_count_parse_error")

    if start_time is not None and end_time is not None and duration is not None:
        derived = end_time - start_time
        if derived < 0:
            suspect_reasons.append("negative_start_end_duration")
        elif abs(derived - duration) > 1.0:
            info_flags.append("duration_mismatch_start_end_gt_1s")

    return {
        "split": split,
        "line_no": row.get("_line_no"),
        "segment_id": segment_id,
        "duration_seconds": duration,
        "start_time": start_time,
        "end_time": end_time,
        "text_len": text_len,
        "word_count": word_count,
        "english_token_count": english_token_count,
        "number_count": number_count,
        "cs_terms_count": cs_terms_count,
        "cs_terms_count_given": cs_terms_count_given,
        "cs_terms_list_size": len(cs_terms),
        "topic": topic,
        "audio_present": audio_present,
        "has_original_video_link": bool(row.get("original_video_link")),
        "has_original_video_title": bool(row.get("original_video_title")),
        "suspect": bool(suspect_reasons),
        "suspect_reasons": ";".join(suspect_reasons),
        "info_flags": ";".join(info_flags),
        "segment_text_preview": text[:160],
        "cs_terms_preview": ";".join(cs_terms[:20]),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not fieldnames:
        keys = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    keys.append(key)
                    seen.add(key)
        fieldnames = keys

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_split(split: str, manifest_path: Path, rows: list[dict[str, Any]], audits: list[dict[str, Any]]) -> dict[str, Any]:
    durations = [a["duration_seconds"] for a in audits if isinstance(a.get("duration_seconds"), (int, float))]
    word_counts = [float(a["word_count"]) for a in audits]
    text_lens = [float(a["text_len"]) for a in audits]
    english_counts = [float(a["english_token_count"]) for a in audits]
    cs_counts = [float(a["cs_terms_count"]) for a in audits if a.get("cs_terms_count") is not None]

    field_presence = {}
    for field in EXPECTED_FIELDS:
        field_presence[field] = sum(1 for r in rows if r.get(field) not in [None, ""])

    schema_keys_counter = Counter()
    for r in rows[:200]:
        schema_keys_counter.update(k for k in r.keys() if not k.startswith("_"))

    suspect_count = sum(1 for a in audits if a["suspect"])

    duration_desc = describe_numeric(durations)
    word_desc = describe_numeric(word_counts)
    text_desc = describe_numeric(text_lens)
    english_desc = describe_numeric(english_counts)
    cs_desc = describe_numeric(cs_counts)

    summary = {
        "split": split,
        "manifest_path": str(manifest_path),
        "rows": len(rows),
        "total_hours": round(sum(durations) / 3600, 4) if durations else None,
        "suspect_samples": suspect_count,
        "suspect_rate": round(suspect_count / len(audits), 4) if audits else None,
        "duration_count": len(durations),
        "duration_min": duration_desc["min"],
        "duration_p10": duration_desc["p10"],
        "duration_median": duration_desc["median"],
        "duration_mean": duration_desc["mean"],
        "duration_p90": duration_desc["p90"],
        "duration_max": duration_desc["max"],
        "word_count_median": word_desc["median"],
        "word_count_mean": word_desc["mean"],
        "text_len_median": text_desc["median"],
        "text_len_mean": text_desc["mean"],
        "english_token_mean": english_desc["mean"],
        "cs_terms_mean": cs_desc["mean"],
        "audio_present_count": sum(1 for a in audits if a["audio_present"]),
        "field_presence": field_presence,
        "observed_schema_keys_top": dict(schema_keys_counter.most_common(50)),
    }

    return summary


def build_topic_summary(audits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: dict[tuple[str, str], int] = defaultdict(int)

    for a in audits:
        counter[(a["split"], a["topic"])] += 1

    rows = [
        {"split": split, "topic": topic, "count": count}
        for (split, topic), count in counter.items()
    ]

    rows.sort(key=lambda x: (x["split"], -x["count"], x["topic"]))
    return rows


def build_cs_term_summary(audits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: dict[tuple[str, str], int] = defaultdict(int)

    for a in audits:
        terms = [x.strip() for x in a.get("cs_terms_preview", "").split(";") if x.strip()]
        for term in terms:
            counter[(a["split"], term)] += 1

    rows = [
        {"split": split, "cs_term": term, "count": count}
        for (split, term), count in counter.items()
    ]

    rows.sort(key=lambda x: (x["split"], -x["count"], x["cs_term"]))
    return rows


def render_markdown_report(
    summaries: list[dict[str, Any]],
    output_dir: Path,
    suspect_reason_counter: Counter,
    info_flag_counter: Counter,
) -> str:
    lines: list[str] = []

    lines.append("# ViMedCSS Sample-based Data Audit Report")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Audit existing ViMedCSS manifests before subset creation and progressive fine-tuning.")
    lines.append("")
    lines.append("This phase does not train models, does not materialize audio, and does not use GPU.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("- `vimedcss_audit_summary.csv`")
    lines.append("- `vimedcss_audit_samples.csv`")
    lines.append("- `vimedcss_suspect_samples.csv`")
    lines.append("- `vimedcss_topic_summary.csv`")
    lines.append("- `vimedcss_cs_term_summary.csv`")
    lines.append("- `vimedcss_schema_examples.json`")
    lines.append("- `vimedcss_audit_summary.json`")
    lines.append("")

    lines.append("## Split summary")
    lines.append("")
    lines.append("| Split | Rows | Total hours | Mean duration | Median duration | Mean words | Mean CS terms | Suspect samples | Suspect rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for s in summaries:
        lines.append(
            f"| {s['split']} | "
            f"{s['rows']} | "
            f"{s['total_hours']} | "
            f"{s['duration_mean']} | "
            f"{s['duration_median']} | "
            f"{s['word_count_mean']} | "
            f"{s['cs_terms_mean']} | "
            f"{s['suspect_samples']} | "
            f"{s['suspect_rate']} |"
        )

    lines.append("")
    lines.append("## Manifest paths")
    lines.append("")
    lines.append("| Split | Manifest |")
    lines.append("|---|---|")
    for s in summaries:
        lines.append(f"| {s['split']} | `{s['manifest_path']}` |")

    lines.append("")
    lines.append("## Field presence")
    lines.append("")
    lines.append("Counts below show how many rows have non-empty values for each expected field.")
    lines.append("")

    for s in summaries:
        lines.append(f"### {s['split']}")
        lines.append("")
        lines.append("| Field | Present rows |")
        lines.append("|---|---:|")
        for field, count in s["field_presence"].items():
            lines.append(f"| `{field}` | {count} |")
        lines.append("")

    lines.append("## Suspect reasons")
    lines.append("")
    if suspect_reason_counter:
        lines.append("| Reason | Count |")
        lines.append("|---|---:|")
        for reason, count in suspect_reason_counter.most_common():
            lines.append(f"| `{reason}` | {count} |")
    else:
        lines.append("No suspect samples found.")
    lines.append("")

    lines.append("## Info flags (non-blocking)")
    lines.append("")
    lines.append("These flags are informational and do not mark samples as suspect.")
    lines.append("")
    if info_flag_counter:
        lines.append("| Flag | Count |")
        lines.append("|---|---:|")
        for flag, count in info_flag_counter.most_common():
            lines.append(f"| `{flag}` | {count} |")
    else:
        lines.append("No info flags.")
    lines.append("")

    lines.append("## Schema examples")
    lines.append("")
    lines.append("Saved to:")
    lines.append("")
    lines.append("```text")
    lines.append(str(output_dir / "vimedcss_schema_examples.json"))
    lines.append("```")
    lines.append("")

    lines.append("## Decision guidance")
    lines.append("")
    lines.append("Proceed to Phase 2 if:")
    lines.append("")
    lines.append("```text")
    lines.append("1. Raw manifests are present.")
    lines.append("2. audio and segment_text fields exist.")
    lines.append("3. Suspect samples are identified, not silently ignored.")
    lines.append("4. Official splits are preserved.")
    lines.append("```")
    lines.append("")
    lines.append("Do not proceed to training if:")
    lines.append("")
    lines.append("```text")
    lines.append("1. train/validation/test/hard manifests are missing.")
    lines.append("2. segment_text is missing for many rows.")
    lines.append("3. audio field is missing for many rows.")
    lines.append("4. suspect rate is extremely high and unexplained.")
    lines.append("```")
    lines.append("")

    lines.append("## Next phase")
    lines.append("")
    lines.append("Phase 2 should create run manifests and subset archives for Run 0, Run A, Run B, and Run C.")
    lines.append("")
    lines.append("Recommended next script:")
    lines.append("")
    lines.append("```text")
    lines.append("scripts/vimedcss/02_create_vimedcss_run_manifests_and_archives.py")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--vimedcss_root",
        required=True,
        help="Path to experiments/asr/vimedcss.",
    )

    parser.add_argument(
        "--output_dir",
        default=None,
        help="Output directory. Defaults to <vimedcss_root>/data_audit.",
    )

    parser.add_argument(
        "--max_schema_examples",
        type=int,
        default=3,
        help="Number of example rows to store per split.",
    )

    args = parser.parse_args()

    vimedcss_root = Path(args.vimedcss_root)
    output_dir = Path(args.output_dir) if args.output_dir else vimedcss_root / "data_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_audits: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    schema_examples: dict[str, Any] = {}
    suspect_reason_counter: Counter = Counter()
    info_flag_counter: Counter = Counter()

    for split in SPLITS:
        manifest_path = detect_manifest_path(vimedcss_root, split)
        rows = read_jsonl(manifest_path)

        audits = [build_sample_audit(row, split) for row in rows]
        all_audits.extend(audits)

        for a in audits:
            if a["suspect_reasons"]:
                for reason in a["suspect_reasons"].split(";"):
                    if reason:
                        suspect_reason_counter[reason] += 1
            if a.get("info_flags"):
                for flag in a["info_flags"].split(";"):
                    if flag:
                        info_flag_counter[flag] += 1

        summaries.append(
            summarize_split(
                split=split,
                manifest_path=manifest_path,
                rows=rows,
                audits=audits,
            )
        )

        schema_examples[split] = {
            "manifest_path": str(manifest_path),
            "rows": len(rows),
            "examples": [
                {k: v for k, v in row.items() if not k.startswith("_")}
                for row in rows[: args.max_schema_examples]
            ],
        }

    suspect_rows = [a for a in all_audits if a["suspect"]]
    topic_summary = build_topic_summary(all_audits)
    cs_term_summary = build_cs_term_summary(all_audits)

    sample_fields = [
        "split",
        "line_no",
        "segment_id",
        "duration_seconds",
        "start_time",
        "end_time",
        "text_len",
        "word_count",
        "english_token_count",
        "number_count",
        "cs_terms_count",
        "cs_terms_count_given",
        "cs_terms_list_size",
        "topic",
        "audio_present",
        "has_original_video_link",
        "has_original_video_title",
        "suspect",
        "suspect_reasons",
        "info_flags",
        "segment_text_preview",
        "cs_terms_preview",
    ]

    summary_fields = [
        "split",
        "manifest_path",
        "rows",
        "total_hours",
        "suspect_samples",
        "suspect_rate",
        "duration_count",
        "duration_min",
        "duration_p10",
        "duration_median",
        "duration_mean",
        "duration_p90",
        "duration_max",
        "word_count_median",
        "word_count_mean",
        "text_len_median",
        "text_len_mean",
        "english_token_mean",
        "cs_terms_mean",
        "audio_present_count",
        "field_presence",
        "observed_schema_keys_top",
    ]

    write_csv(output_dir / "vimedcss_audit_samples.csv", all_audits, sample_fields)
    write_csv(output_dir / "vimedcss_suspect_samples.csv", suspect_rows, sample_fields)
    write_csv(output_dir / "vimedcss_audit_summary.csv", summaries, summary_fields)
    write_csv(output_dir / "vimedcss_topic_summary.csv", topic_summary)
    write_csv(output_dir / "vimedcss_cs_term_summary.csv", cs_term_summary)
    write_json(output_dir / "vimedcss_schema_examples.json", schema_examples)

    summary_json = {
        "created_at": now_iso(),
        "vimedcss_root": str(vimedcss_root),
        "output_dir": str(output_dir),
        "splits": summaries,
        "suspect_reason_counts": dict(suspect_reason_counter),
        "info_flag_counts": dict(info_flag_counter),
        "total_rows": sum(s["rows"] for s in summaries),
        "total_suspect_samples": len(suspect_rows),
        "phase": "phase1_sample_based_audit",
        "does_not_train": True,
        "does_not_materialize_audio": True,
        "does_not_use_gpu": True,
    }

    write_json(output_dir / "vimedcss_audit_summary.json", summary_json)

    report = render_markdown_report(
        summaries=summaries,
        output_dir=output_dir,
        suspect_reason_counter=suspect_reason_counter,
        info_flag_counter=info_flag_counter,
    )

    report_path = output_dir / "AUDIT_VIMEDCSS_SAMPLE_BASED_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    print(json.dumps(
        {
            "status": "DONE",
            "output_dir": str(output_dir),
            "report": str(report_path),
            "summary_csv": str(output_dir / "vimedcss_audit_summary.csv"),
            "samples_csv": str(output_dir / "vimedcss_audit_samples.csv"),
            "suspect_csv": str(output_dir / "vimedcss_suspect_samples.csv"),
            "summary_json": str(output_dir / "vimedcss_audit_summary.json"),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()