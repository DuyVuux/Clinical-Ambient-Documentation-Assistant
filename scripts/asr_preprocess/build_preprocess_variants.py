#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build ASR audio preprocessing variants for VietMed dev set.

Day 2 Week 4 objective:
- Create versioned preprocessing variants.
- Do not modify Bronze/Silver source audio.
- Do not touch test_holdout.
- Write one manifest JSONL per variant.

Variants:
- p00_format_only
- p10_edge_pad_200ms
- p11_edge_pad_300ms
- p12_edge_pad_500ms
- p03_vad_pad_200ms
- p04_vad_pad_300ms
- p05_vad_pad_500ms

Example:

python scripts/asr_preprocess/build_preprocess_variants.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant" \
  --variants p00_format_only p10_edge_pad_200ms p11_edge_pad_300ms p12_edge_pad_500ms

If Silero VAD is available:

python scripts/asr_preprocess/build_preprocess_variants.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --project_root "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant" \
  --variants p03_vad_pad_200ms p04_vad_pad_300ms p05_vad_pad_500ms \
  --enable_vad
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from tqdm import tqdm


DEFAULT_PROJECT_ROOT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)

TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
TARGET_SUBTYPE = "PCM_16"

VARIANT_CONFIGS = {
    "p00_format_only": {
        "kind": "format_only",
        "edge_pad_ms": 0,
        "vad": False,
    },
    "p10_edge_pad_200ms": {
        "kind": "edge_pad_only",
        "edge_pad_ms": 200,
        "vad": False,
    },
    "p11_edge_pad_300ms": {
        "kind": "edge_pad_only",
        "edge_pad_ms": 300,
        "vad": False,
    },
    "p12_edge_pad_500ms": {
        "kind": "edge_pad_only",
        "edge_pad_ms": 500,
        "vad": False,
    },
    "p03_vad_pad_200ms": {
        "kind": "vad_pad",
        "edge_pad_ms": 200,
        "vad": True,
    },
    "p04_vad_pad_300ms": {
        "kind": "vad_pad",
        "edge_pad_ms": 300,
        "vad": True,
    },
    "p05_vad_pad_500ms": {
        "kind": "vad_pad",
        "edge_pad_ms": 500,
        "vad": True,
    },
}


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
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc

    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def resolve_audio_path(row: dict[str, Any], project_root: Path) -> Path:
    for key in ["clean_audio_path", "preprocessed_audio_path", "raw_audio_path", "audio"]:
        value = row.get(key)

        if isinstance(value, str) and value.strip():
            path = Path(value)
            return path if path.is_absolute() else project_root / path

    raise KeyError(
        "Cannot find audio path in row. Expected one of: "
        "clean_audio_path, preprocessed_audio_path, raw_audio_path, audio."
    )


def safe_rel(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        mono = audio
    elif audio.ndim == 2:
        mono = np.mean(audio, axis=1)
    else:
        raise ValueError(f"Unsupported audio shape: {audio.shape}")

    mono = mono.astype(np.float32)
    mono = np.nan_to_num(mono, nan=0.0, posinf=0.0, neginf=0.0)
    return mono


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    if orig_sr == target_sr:
        return audio.astype(np.float32)

    gcd = math.gcd(orig_sr, target_sr)
    up = target_sr // gcd
    down = orig_sr // gcd

    resampled = resample_poly(audio, up, down)
    return resampled.astype(np.float32)


def load_audio_16k_mono(audio_path: Path) -> tuple[np.ndarray, int, dict[str, Any]]:
    audio, sr = sf.read(str(audio_path), always_2d=False)
    original_shape = list(audio.shape) if isinstance(audio, np.ndarray) else None

    mono = to_mono(audio)
    mono_16k = resample_audio(mono, sr, TARGET_SAMPLE_RATE)

    metadata = {
        "original_sample_rate_hz": int(sr),
        "original_shape": original_shape,
        "target_sample_rate_hz": TARGET_SAMPLE_RATE,
        "target_channels": TARGET_CHANNELS,
    }

    return mono_16k, TARGET_SAMPLE_RATE, metadata


def add_silence_padding(audio: np.ndarray, sample_rate: int, pad_ms: int) -> np.ndarray:
    if pad_ms <= 0:
        return audio

    pad_samples = int(sample_rate * pad_ms / 1000)
    silence = np.zeros(pad_samples, dtype=np.float32)

    return np.concatenate([silence, audio, silence])


def save_wav(audio: np.ndarray, sample_rate: int, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Safety clamp for PCM 16 writing.
    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)

    sf.write(
        str(output_path),
        audio,
        sample_rate,
        subtype=TARGET_SUBTYPE,
    )


def try_load_silero_vad():
    try:
        import torch

        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=False,
            trust_repo=True,
        )

        get_speech_timestamps = utils[0]

        return {
            "torch": torch,
            "model": model,
            "get_speech_timestamps": get_speech_timestamps,
            "available": True,
            "error": None,
        }

    except Exception as exc:
        return {
            "torch": None,
            "model": None,
            "get_speech_timestamps": None,
            "available": False,
            "error": str(exc),
        }


def vad_trim_with_padding(
    audio: np.ndarray,
    sample_rate: int,
    pad_ms: int,
    vad_runtime: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Conservative VAD:
    - If VAD fails, return edge padding only.
    - If VAD gives invalid/too-short segment, return edge padding only.
    - Merge all speech timestamps from first speech start to last speech end.
    """

    if not vad_runtime.get("available"):
        fallback = add_silence_padding(audio, sample_rate, pad_ms)
        return fallback, {
            "vad_used": False,
            "vad_fallback": True,
            "vad_reason": f"silero_unavailable: {vad_runtime.get('error')}",
            "speech_start_sample": None,
            "speech_end_sample": None,
        }

    try:
        torch = vad_runtime["torch"]
        model = vad_runtime["model"]
        get_speech_timestamps = vad_runtime["get_speech_timestamps"]

        tensor = torch.from_numpy(audio)

        timestamps = get_speech_timestamps(
            tensor,
            model,
            sampling_rate=sample_rate,
            min_speech_duration_ms=250,
            min_silence_duration_ms=100,
            speech_pad_ms=0,
            return_seconds=False,
        )

        if not timestamps:
            fallback = add_silence_padding(audio, sample_rate, pad_ms)
            return fallback, {
                "vad_used": True,
                "vad_fallback": True,
                "vad_reason": "no_speech_detected",
                "speech_start_sample": None,
                "speech_end_sample": None,
            }

        speech_start = int(timestamps[0]["start"])
        speech_end = int(timestamps[-1]["end"])

        if speech_end <= speech_start:
            fallback = add_silence_padding(audio, sample_rate, pad_ms)
            return fallback, {
                "vad_used": True,
                "vad_fallback": True,
                "vad_reason": "invalid_vad_span",
                "speech_start_sample": speech_start,
                "speech_end_sample": speech_end,
            }

        pad_samples = int(sample_rate * pad_ms / 1000)

        start = max(0, speech_start - pad_samples)
        end = min(len(audio), speech_end + pad_samples)

        # Safety: if VAD would remove too much, fallback.
        kept_ratio = (end - start) / max(len(audio), 1)
        if kept_ratio < 0.50:
            fallback = add_silence_padding(audio, sample_rate, pad_ms)
            return fallback, {
                "vad_used": True,
                "vad_fallback": True,
                "vad_reason": f"kept_ratio_too_low:{kept_ratio:.4f}",
                "speech_start_sample": speech_start,
                "speech_end_sample": speech_end,
                "kept_ratio": kept_ratio,
            }

        trimmed = audio[start:end]

        return trimmed, {
            "vad_used": True,
            "vad_fallback": False,
            "vad_reason": "ok",
            "speech_start_sample": speech_start,
            "speech_end_sample": speech_end,
            "trim_start_sample": start,
            "trim_end_sample": end,
            "kept_ratio": kept_ratio,
            "num_speech_segments": len(timestamps),
        }

    except Exception as exc:
        fallback = add_silence_padding(audio, sample_rate, pad_ms)

        return fallback, {
            "vad_used": True,
            "vad_fallback": True,
            "vad_reason": f"exception:{exc}",
            "speech_start_sample": None,
            "speech_end_sample": None,
        }


def get_output_audio_path(
    project_root: Path,
    variant_name: str,
    sample_id: str,
) -> Path:
    return (
        project_root
        / "data"
        / "data_lake"
        / "silver"
        / "audio_preprocessed"
        / variant_name
        / f"{sample_id}_{variant_name}.wav"
    )


def get_output_manifest_path(project_root: Path, input_manifest: Path, variant_name: str) -> Path:
    # Example:
    # vietmed_dev_v0_1.jsonl -> vietmed_dev_p11_edge_pad_300ms.jsonl
    stem = input_manifest.stem
    if stem.endswith("_v0_1"):
        stem = stem.replace("_v0_1", "")

    return (
        project_root
        / "data"
        / "data_lake"
        / "silver"
        / "asr_manifests"
        / "preprocessing_variants"
        / f"{stem}_{variant_name}.jsonl"
    )


def process_one_variant(
    rows: list[dict[str, Any]],
    variant_name: str,
    input_manifest: Path,
    project_root: Path,
    vad_runtime: dict[str, Any],
) -> dict[str, Any]:
    config = VARIANT_CONFIGS[variant_name]

    output_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for row in tqdm(rows, desc=f"Building {variant_name}"):
        sample_id = row.get("sample_id")

        if not sample_id:
            failures.append({
                "sample_id": None,
                "error": "missing_sample_id",
                "row": row,
            })
            continue

        try:
            input_audio_path = resolve_audio_path(row, project_root)
            audio, sample_rate, load_meta = load_audio_16k_mono(input_audio_path)

            original_duration = len(audio) / sample_rate

            pad_ms = int(config["edge_pad_ms"])

            if config["kind"] == "format_only":
                processed = audio
                preprocess_meta = {
                    "operation": "format_only",
                    "edge_pad_ms": 0,
                    "vad_enabled": False,
                    "vad_fallback": False,
                }

            elif config["kind"] == "edge_pad_only":
                processed = add_silence_padding(audio, sample_rate, pad_ms)
                preprocess_meta = {
                    "operation": "edge_pad_only",
                    "edge_pad_ms": pad_ms,
                    "vad_enabled": False,
                    "vad_fallback": False,
                }

            elif config["kind"] == "vad_pad":
                processed, vad_meta = vad_trim_with_padding(
                    audio=audio,
                    sample_rate=sample_rate,
                    pad_ms=pad_ms,
                    vad_runtime=vad_runtime,
                )
                preprocess_meta = {
                    "operation": "vad_pad",
                    "edge_pad_ms": pad_ms,
                    "vad_enabled": True,
                    **vad_meta,
                }

            else:
                raise ValueError(f"Unsupported variant kind: {config['kind']}")

            processed_duration = len(processed) / sample_rate

            output_audio_path = get_output_audio_path(
                project_root=project_root,
                variant_name=variant_name,
                sample_id=sample_id,
            )

            save_wav(processed, sample_rate, output_audio_path)

            checksum = sha256_file(output_audio_path)

            output_row = {
                **row,
                "source_clean_audio_path": row.get("clean_audio_path"),
                "preprocessed_audio_path": safe_rel(output_audio_path, project_root),
                "clean_audio_path": safe_rel(output_audio_path, project_root),
                "preprocessing_version": variant_name,
                "preprocessing_config": {
                    "sample_rate_hz": TARGET_SAMPLE_RATE,
                    "channels": TARGET_CHANNELS,
                    "encoding": TARGET_SUBTYPE,
                    **preprocess_meta,
                },
                "original_duration_seconds": round(original_duration, 4),
                "processed_duration_seconds": round(processed_duration, 4),
                "duration_delta_seconds": round(processed_duration - original_duration, 4),
                "preprocessed_checksum_sha256": checksum,
                "preprocessed_created_at": now_iso(),
                "preprocessed_created_by": "Duy",
                "preprocessed_version": "v0.1.0",
                "audio_load_metadata": load_meta,
            }

            output_rows.append(output_row)

        except Exception as exc:
            failures.append({
                "sample_id": sample_id,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            })

    output_manifest_path = get_output_manifest_path(
        project_root=project_root,
        input_manifest=input_manifest,
        variant_name=variant_name,
    )

    write_jsonl(output_manifest_path, output_rows)

    failure_path = (
        project_root
        / "experiments"
        / "asr"
        / "preprocessing"
        / "day2_build_variants"
        / f"{variant_name}_failures.jsonl"
    )
    write_jsonl(failure_path, failures)

    summary = {
        "variant": variant_name,
        "input_manifest": safe_rel(input_manifest, project_root),
        "output_manifest": safe_rel(output_manifest_path, project_root),
        "n_input_rows": len(rows),
        "n_output_rows": len(output_rows),
        "n_failures": len(failures),
        "failure_path": safe_rel(failure_path, project_root),
    }

    summary_path = (
        project_root
        / "experiments"
        / "asr"
        / "preprocessing"
        / "day2_build_variants"
        / f"{variant_name}_summary.json"
    )
    write_json(summary_path, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return summary


def build_day2_markdown_report(project_root: Path, summaries: list[dict[str, Any]]) -> None:
    report_path = (
        project_root
        / "experiments"
        / "asr"
        / "preprocessing"
        / "day2_build_variants"
        / "DAY2_BUILD_PREPROCESSING_VARIANTS_REPORT.md"
    )

    lines: list[str] = []
    lines.append("# Day 2 Week 4 — Build ASR Preprocessing Variants")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Create versioned audio preprocessing variants for VietMed dev set.")
    lines.append("")
    lines.append("## Variants")
    lines.append("")
    lines.append("| Variant | Input rows | Output rows | Failures | Manifest |")
    lines.append("|---|---:|---:|---:|---|")

    for s in summaries:
        lines.append(
            f"| {s['variant']} | {s['n_input_rows']} | {s['n_output_rows']} | "
            f"{s['n_failures']} | `{s['output_manifest']}` |"
        )

    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- Raw audio was not modified.")
    lines.append("- Test holdout was not used.")
    lines.append("- Each variant has its own manifest.")
    lines.append("- Each preprocessed file has checksum metadata.")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append("Run `audit_audio_quality.py` on each variant manifest in Day 3.")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[DONE] Day 2 report: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build preprocessing variants for ASR audio."
    )

    parser.add_argument(
        "--manifest",
        required=True,
        help="Input ASR manifest JSONL, usually VietMed dev split.",
    )

    parser.add_argument(
        "--project_root",
        default=str(DEFAULT_PROJECT_ROOT),
        help="Project root path.",
    )

    parser.add_argument(
        "--variants",
        nargs="+",
        required=True,
        choices=list(VARIANT_CONFIGS.keys()),
        help="Preprocessing variants to build.",
    )

    parser.add_argument(
        "--enable_vad",
        action="store_true",
        help="Enable Silero VAD for VAD-based variants.",
    )

    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="Optional debug limit.",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)
    manifest_path = Path(args.manifest)

    if not manifest_path.is_absolute():
        manifest_path = project_root / manifest_path

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    rows = read_jsonl(manifest_path)

    if args.max_samples is not None:
        rows = rows[: args.max_samples]

    vad_runtime = {
        "available": False,
        "error": "VAD not enabled",
    }

    if args.enable_vad:
        print("[INFO] Loading Silero VAD...")
        vad_runtime = try_load_silero_vad()
        print(f"[INFO] Silero VAD available: {vad_runtime.get('available')}")
        if not vad_runtime.get("available"):
            print(f"[WARN] Silero VAD error: {vad_runtime.get('error')}")
            print("[WARN] VAD variants will fallback to edge padding only.")

    summaries = []

    for variant_name in args.variants:
        summaries.append(
            process_one_variant(
                rows=rows,
                variant_name=variant_name,
                input_manifest=manifest_path,
                project_root=project_root,
                vad_runtime=vad_runtime,
            )
        )

    build_day2_markdown_report(project_root, summaries)


if __name__ == "__main__":
    main()