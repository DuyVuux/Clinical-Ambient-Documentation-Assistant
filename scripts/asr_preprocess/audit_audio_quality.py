#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audit audio quality for ASR preprocessing.

Purpose:
- Detect audio problems before fine-tuning or preprocessing.
- Measure duration, RMS, peak, clipping, silence, and edge-energy risk.
- Identify samples that may cause beginning/end word loss.

Example:

python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/dev \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"

For train:

python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/train \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


DEFAULT_PROJECT_ROOT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)

EPS = 1e-12


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc

    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_relative_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def resolve_audio_path(row: dict[str, Any], project_root: Path) -> Path:
    """
    Priority:
    1. clean_audio_path
    2. preprocessed_audio_path
    3. raw_audio_path
    4. audio
    """

    for key in ["clean_audio_path", "preprocessed_audio_path", "raw_audio_path", "audio"]:
        value = row.get(key)

        if isinstance(value, str) and value.strip():
            path = Path(value)

            if path.is_absolute():
                return path

            return project_root / path

    raise KeyError(
        "Cannot find audio path in manifest row. "
        "Expected one of: clean_audio_path, preprocessed_audio_path, raw_audio_path, audio."
    )


def to_mono_float(audio: np.ndarray) -> np.ndarray:
    """
    Convert audio array to mono float32 in [-1, 1]-like range.
    soundfile usually returns float64 for floating read.
    """

    if audio.ndim == 1:
        mono = audio
    elif audio.ndim == 2:
        mono = np.mean(audio, axis=1)
    else:
        raise ValueError(f"Unsupported audio shape: {audio.shape}")

    mono = mono.astype(np.float32)

    # Replace NaN/Inf to avoid metric explosion.
    mono = np.nan_to_num(mono, nan=0.0, posinf=0.0, neginf=0.0)

    return mono


def rms(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x)) + EPS))


def amplitude_to_db(value: float) -> float:
    return float(20.0 * math.log10(max(value, EPS)))


def compute_silence_ms(
    audio: np.ndarray,
    sample_rate: int,
    threshold_db: float = -40.0,
    from_start: bool = True,
) -> float:
    """
    Estimate leading/trailing silence using frame RMS.
    This is a simple heuristic, not a replacement for VAD.

    threshold_db:
    - -40 dB is reasonably conservative for silence detection.
    """

    if audio.size == 0:
        return 0.0

    frame_ms = 20
    frame_len = max(1, int(sample_rate * frame_ms / 1000))

    if from_start:
        indices = range(0, len(audio), frame_len)
    else:
        indices = range(len(audio), 0, -frame_len)

    silence_frames = 0

    for idx in indices:
        if from_start:
            frame = audio[idx : idx + frame_len]
        else:
            start = max(0, idx - frame_len)
            frame = audio[start:idx]

        if frame.size == 0:
            continue

        frame_db = amplitude_to_db(rms(frame))

        if frame_db < threshold_db:
            silence_frames += 1
        else:
            break

    return float(silence_frames * frame_ms)


def slice_ms(audio: np.ndarray, sample_rate: int, start_ms: float, end_ms: float) -> np.ndarray:
    start = max(0, int(sample_rate * start_ms / 1000))
    end = min(len(audio), int(sample_rate * end_ms / 1000))

    if end <= start:
        return np.array([], dtype=np.float32)

    return audio[start:end]


def compute_edge_metrics(
    audio: np.ndarray,
    sample_rate: int,
    edge_ms: int = 300,
) -> dict[str, float]:
    duration_ms = 1000.0 * len(audio) / sample_rate if sample_rate > 0 else 0.0

    first = slice_ms(audio, sample_rate, 0, min(edge_ms, duration_ms))
    last = slice_ms(audio, sample_rate, max(0, duration_ms - edge_ms), duration_ms)

    # Middle segment excludes first and last edge windows when possible.
    if duration_ms > 2 * edge_ms:
        middle = slice_ms(audio, sample_rate, edge_ms, duration_ms - edge_ms)
    else:
        middle = audio

    first_rms = rms(first)
    last_rms = rms(last)
    middle_rms = rms(middle)

    first_db = amplitude_to_db(first_rms)
    last_db = amplitude_to_db(last_rms)
    middle_db = amplitude_to_db(middle_rms)

    first_to_middle_ratio = first_rms / max(middle_rms, EPS)
    last_to_middle_ratio = last_rms / max(middle_rms, EPS)
    min_edge_to_middle_ratio = min(first_to_middle_ratio, last_to_middle_ratio)

    return {
        "first_300ms_rms": first_rms,
        "last_300ms_rms": last_rms,
        "middle_rms": middle_rms,
        "first_300ms_db": first_db,
        "last_300ms_db": last_db,
        "middle_db": middle_db,
        "first_to_middle_ratio": float(first_to_middle_ratio),
        "last_to_middle_ratio": float(last_to_middle_ratio),
        "min_edge_to_middle_ratio": float(min_edge_to_middle_ratio),
    }


def compute_audio_metrics(audio_path: Path) -> dict[str, Any]:
    audio, sample_rate = sf.read(str(audio_path), always_2d=False)

    channels = 1
    if isinstance(audio, np.ndarray) and audio.ndim == 2:
        channels = audio.shape[1]

    mono = to_mono_float(audio)

    duration_seconds = float(len(mono) / sample_rate) if sample_rate > 0 else 0.0

    peak = float(np.max(np.abs(mono))) if mono.size else 0.0
    rms_value = rms(mono)

    # Clipping proxy for float PCM normalized audio.
    # If original audio is int PCM read by soundfile as float, clipped samples often appear near +/-1.
    clipping_ratio = float(np.mean(np.abs(mono) >= 0.999)) if mono.size else 0.0

    leading_silence_ms = compute_silence_ms(
        mono,
        sample_rate,
        threshold_db=-40.0,
        from_start=True,
    )
    trailing_silence_ms = compute_silence_ms(
        mono,
        sample_rate,
        threshold_db=-40.0,
        from_start=False,
    )

    edge_metrics = compute_edge_metrics(mono, sample_rate, edge_ms=300)

    return {
        "sample_rate_hz": int(sample_rate),
        "channels": int(channels),
        "duration_seconds": round(duration_seconds, 4),
        "rms": rms_value,
        "rms_db": amplitude_to_db(rms_value),
        "peak": peak,
        "peak_db": amplitude_to_db(peak),
        "clipping_ratio": clipping_ratio,
        "leading_silence_ms": leading_silence_ms,
        "trailing_silence_ms": trailing_silence_ms,
        **edge_metrics,
    }


def classify_warnings(metrics: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    duration = metrics["duration_seconds"]
    sample_rate = metrics["sample_rate_hz"]
    channels = metrics["channels"]
    rms_db = metrics["rms_db"]
    peak_db = metrics["peak_db"]
    clipping_ratio = metrics["clipping_ratio"]
    leading_silence_ms = metrics["leading_silence_ms"]
    trailing_silence_ms = metrics["trailing_silence_ms"]
    edge_ratio = metrics["min_edge_to_middle_ratio"]

    if sample_rate != 16000:
        warnings.append("non_16khz")

    if channels != 1:
        warnings.append("non_mono")

    if duration < 1.0:
        warnings.append("too_short")

    if duration > 30.0:
        warnings.append("long_audio_may_need_chunking")

    if rms_db < -35.0:
        warnings.append("too_quiet")

    if rms_db > -10.0:
        warnings.append("too_loud")

    if peak_db > -0.1:
        warnings.append("peak_near_0db_clipping_risk")

    if clipping_ratio > 0.001:
        warnings.append("clipping_detected")

    if leading_silence_ms > 1000:
        warnings.append("long_leading_silence")

    if trailing_silence_ms > 1000:
        warnings.append("long_trailing_silence")

    if edge_ratio < 0.35:
        warnings.append("edge_loss_risk")

    return warnings


def summarize_numeric(values: list[float]) -> dict[str, float | None]:
    clean = [v for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]

    if not clean:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "p10": None,
            "p90": None,
        }

    arr = np.array(clean, dtype=np.float64)

    return {
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "mean": round(float(np.mean(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "p10": round(float(np.percentile(arr, 10)), 4),
        "p90": round(float(np.percentile(arr, 90)), 4),
    }


def build_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    warning_counts: dict[str, int] = {}

    for item in items:
        for warning in item.get("warnings", []):
            warning_counts[warning] = warning_counts.get(warning, 0) + 1

    metric_keys = [
        "duration_seconds",
        "rms_db",
        "peak_db",
        "clipping_ratio",
        "leading_silence_ms",
        "trailing_silence_ms",
        "first_300ms_db",
        "last_300ms_db",
        "middle_db",
        "min_edge_to_middle_ratio",
    ]

    numeric_summary = {
        key: summarize_numeric([item["metrics"].get(key) for item in items])
        for key in metric_keys
    }

    return {
        "n_samples": len(items),
        "warning_counts": dict(sorted(warning_counts.items())),
        "numeric_summary": numeric_summary,
    }


def render_markdown_report(
    manifest_path: Path,
    report_json_path: Path,
    edge_risk_path: Path,
    summary: dict[str, Any],
) -> str:
    warning_counts = summary["warning_counts"]
    numeric_summary = summary["numeric_summary"]

    def wc(name: str) -> int:
        return warning_counts.get(name, 0)

    lines: list[str] = []

    lines.append("# Day 1 Week 4 — Audio Quality Audit Report")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Manifest: `{manifest_path}`")
    lines.append(f"- Full JSON report: `{report_json_path}`")
    lines.append(f"- Edge-loss risk samples: `{edge_risk_path}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total samples: **{summary['n_samples']}**")
    lines.append("")
    lines.append("## Warning counts")
    lines.append("")
    lines.append("| Warning | Count | Meaning |")
    lines.append("|---|---:|---|")
    lines.append(f"| non_16khz | {wc('non_16khz')} | Audio is not 16kHz |")
    lines.append(f"| non_mono | {wc('non_mono')} | Audio is not mono |")
    lines.append(f"| too_short | {wc('too_short')} | Duration < 1 second |")
    lines.append(f"| long_audio_may_need_chunking | {wc('long_audio_may_need_chunking')} | Duration > 30 seconds |")
    lines.append(f"| too_quiet | {wc('too_quiet')} | RMS < -35 dB |")
    lines.append(f"| too_loud | {wc('too_loud')} | RMS > -10 dB |")
    lines.append(f"| peak_near_0db_clipping_risk | {wc('peak_near_0db_clipping_risk')} | Peak near 0 dB |")
    lines.append(f"| clipping_detected | {wc('clipping_detected')} | Many samples close to +/-1 |")
    lines.append(f"| long_leading_silence | {wc('long_leading_silence')} | Leading silence > 1000 ms |")
    lines.append(f"| long_trailing_silence | {wc('long_trailing_silence')} | Trailing silence > 1000 ms |")
    lines.append(f"| edge_loss_risk | {wc('edge_loss_risk')} | First/last 300ms much weaker than middle |")
    lines.append("")
    lines.append("## Numeric summary")
    lines.append("")
    lines.append("| Metric | Min | P10 | Median | Mean | P90 | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for metric, stats in numeric_summary.items():
        lines.append(
            f"| {metric} | "
            f"{stats['min']} | {stats['p10']} | {stats['median']} | "
            f"{stats['mean']} | {stats['p90']} | {stats['max']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- `edge_loss_risk` suggests the beginning or ending of the utterance is much weaker than the middle.")
    lines.append("- `long_leading_silence` and `long_trailing_silence` suggest VAD/silence trimming may help.")
    lines.append("- `too_quiet` suggests loudness normalization or light compression may help.")
    lines.append("- `clipping_detected` suggests normalization/compression must be careful because the signal may already be distorted.")
    lines.append("")
    lines.append("## Recommended next step")
    lines.append("")
    lines.append("Create preprocessing variants and evaluate them on the dev set:")
    lines.append("")
    lines.append("- `p00_format_only`")
    lines.append("- `p01_loudnorm`")
    lines.append("- `p02_compressor_loudnorm`")
    lines.append("- `p03_vad_pad_200ms`")
    lines.append("- `p04_vad_pad_300ms`")
    lines.append("- `p05_vad_pad_500ms`")

    return "\n".join(lines) + "\n"


def audit_manifest(
    manifest_path: Path,
    output_dir: Path,
    project_root: Path,
) -> None:
    rows = read_jsonl(manifest_path)

    items: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        sample_id = row.get("sample_id", f"sample_{idx:06d}")

        try:
            audio_path = resolve_audio_path(row, project_root)

            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            metrics = compute_audio_metrics(audio_path)
            warnings = classify_warnings(metrics)

            item = {
                "sample_id": sample_id,
                "source_name": row.get("source_name"),
                "split_role": row.get("split_role"),
                "audio_path": safe_relative_path(audio_path, project_root),
                "transcript_text": row.get("transcript_text", ""),
                "metrics": metrics,
                "warnings": warnings,
            }

            items.append(item)

            print(f"[OK] {idx}/{len(rows)} {sample_id} warnings={warnings}")

        except Exception as exc:
            failed_item = {
                "sample_id": sample_id,
                "error": str(exc),
                "row": row,
            }
            failed.append(failed_item)
            print(f"[FAIL] {idx}/{len(rows)} {sample_id}: {exc}")

    summary = build_summary(items)

    report = {
        "manifest_path": str(manifest_path),
        "output_dir": str(output_dir),
        "summary": summary,
        "items": items,
        "failed": failed,
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    report_json_path = output_dir / "audio_quality_report.json"
    edge_risk_path = output_dir / "edge_loss_risk_samples.jsonl"
    failed_path = output_dir / "failed_audio_quality_audit.jsonl"
    report_md_path = output_dir / "DAY1_AUDIO_QA_REPORT.md"

    edge_risk_items = [
        item for item in items
        if "edge_loss_risk" in item.get("warnings", [])
    ]

    write_json(report_json_path, report)
    write_jsonl(edge_risk_path, edge_risk_items)
    write_jsonl(failed_path, failed)

    md = render_markdown_report(
        manifest_path=manifest_path,
        report_json_path=report_json_path,
        edge_risk_path=edge_risk_path,
        summary=summary,
    )
    report_md_path.write_text(md, encoding="utf-8")

    print("")
    print("[DONE] Audio quality audit completed")
    print(f"Report JSON: {report_json_path}")
    print(f"Report MD:   {report_md_path}")
    print(f"Edge risks:  {edge_risk_path}")
    print(f"Failed:      {failed_path}")
    print("")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit audio quality before ASR preprocessing."
    )

    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to ASR manifest JSONL.",
    )

    parser.add_argument(
        "--output_dir",
        required=True,
        help="Output directory for audit reports.",
    )

    parser.add_argument(
        "--project_root",
        default=str(DEFAULT_PROJECT_ROOT),
        help="Project root path.",
    )

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    project_root = Path(args.project_root)

    if not manifest_path.is_absolute():
        manifest_path = project_root / manifest_path

    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    audit_manifest(
        manifest_path=manifest_path,
        output_dir=output_dir,
        project_root=project_root,
    )


if __name__ == "__main__":
    main()