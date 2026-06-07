#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)

EPS = 1e-12


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def resolve_audio_path(row: dict[str, Any], project_root: Path) -> Path:
    for key in ["preprocessed_audio_path", "clean_audio_path", "raw_audio_path", "audio"]:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            p = Path(value)
            return p if p.is_absolute() else project_root / p
    raise KeyError("No audio path found")


def to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        x = audio
    elif audio.ndim == 2:
        x = np.mean(audio, axis=1)
    else:
        raise ValueError(f"Unsupported audio shape: {audio.shape}")
    return np.nan_to_num(x.astype(np.float32))


def rms(x: np.ndarray) -> float:
    if len(x) == 0:
        return 0.0
    return float(np.sqrt(np.mean(x * x) + EPS))


def db(v: float) -> float:
    return float(20 * math.log10(max(v, EPS)))


def frame_rms_db(audio: np.ndarray, sr: int, frame_ms: int = 20) -> np.ndarray:
    frame_len = max(1, int(sr * frame_ms / 1000))
    vals = []
    for start in range(0, len(audio), frame_len):
        frame = audio[start:start + frame_len]
        if len(frame) == 0:
            continue
        vals.append(db(rms(frame)))
    return np.array(vals, dtype=np.float32)


def detect_speech_region(
    audio: np.ndarray,
    sr: int,
    frame_ms: int = 20,
    threshold_db: float = -40.0,
    min_consecutive_frames: int = 2,
) -> tuple[int, int, dict[str, Any]]:
    """
    Simple energy-based speech region detection.
    It is not VAD, only used to ignore intentionally inserted silence padding.
    """

    frame_len = max(1, int(sr * frame_ms / 1000))
    energies = frame_rms_db(audio, sr, frame_ms)
    active = energies > threshold_db

    if not active.any():
        return 0, len(audio), {
            "speech_detected": False,
            "reason": "no_energy_above_threshold",
            "threshold_db": threshold_db,
        }

    active_idx = np.where(active)[0]

    first = int(active_idx[0])
    last = int(active_idx[-1])

    # Expand slightly to avoid cutting weak speech edge.
    expand_frames = min_consecutive_frames
    first = max(0, first - expand_frames)
    last = min(len(energies) - 1, last + expand_frames)

    start_sample = first * frame_len
    end_sample = min(len(audio), (last + 1) * frame_len)

    return start_sample, end_sample, {
        "speech_detected": True,
        "threshold_db": threshold_db,
        "speech_start_ms": round(start_sample / sr * 1000, 2),
        "speech_end_ms": round(end_sample / sr * 1000, 2),
        "speech_duration_seconds": round((end_sample - start_sample) / sr, 4),
    }


def segment(audio: np.ndarray, sr: int, start_ms: float, end_ms: float) -> np.ndarray:
    start = max(0, int(sr * start_ms / 1000))
    end = min(len(audio), int(sr * end_ms / 1000))
    if end <= start:
        return np.array([], dtype=np.float32)
    return audio[start:end]


def compute_speech_edge_metrics(audio_path: Path) -> dict[str, Any]:
    audio, sr = sf.read(str(audio_path), always_2d=False)
    x = to_mono(audio)

    speech_start, speech_end, speech_meta = detect_speech_region(x, sr)

    speech = x[speech_start:speech_end]
    speech_dur_ms = len(speech) / sr * 1000 if sr else 0

    edge_ms = 300

    if speech_dur_ms <= 2 * edge_ms:
        middle = speech
        first = speech[: int(sr * min(edge_ms, speech_dur_ms) / 1000)]
        last = speech[-int(sr * min(edge_ms, speech_dur_ms) / 1000):]
    else:
        first = speech[: int(sr * edge_ms / 1000)]
        last = speech[-int(sr * edge_ms / 1000):]
        middle = speech[int(sr * edge_ms / 1000): -int(sr * edge_ms / 1000)]

    first_rms = rms(first)
    last_rms = rms(last)
    middle_rms = rms(middle)

    first_ratio = first_rms / max(middle_rms, EPS)
    last_ratio = last_rms / max(middle_rms, EPS)
    min_ratio = min(first_ratio, last_ratio)

    return {
        **speech_meta,
        "sample_rate_hz": sr,
        "duration_seconds": round(len(x) / sr, 4),
        "speech_first_300ms_db": db(first_rms),
        "speech_last_300ms_db": db(last_rms),
        "speech_middle_db": db(middle_rms),
        "speech_first_to_middle_ratio": float(first_ratio),
        "speech_last_to_middle_ratio": float(last_ratio),
        "speech_min_edge_to_middle_ratio": float(min_ratio),
        "speech_edge_loss_risk": bool(min_ratio < 0.35),
    }


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(items)
    risk = sum(1 for x in items if x["metrics"]["speech_edge_loss_risk"])
    ratios = [
        x["metrics"]["speech_min_edge_to_middle_ratio"]
        for x in items
        if isinstance(x["metrics"].get("speech_min_edge_to_middle_ratio"), (int, float))
    ]

    return {
        "n_samples": n,
        "speech_edge_loss_risk": risk,
        "speech_edge_loss_risk_rate": round(risk / n, 4) if n else None,
        "speech_min_edge_to_middle_ratio_mean": round(float(np.mean(ratios)), 4) if ratios else None,
        "speech_min_edge_to_middle_ratio_median": round(float(np.median(ratios)), 4) if ratios else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    args = parser.parse_args()

    project_root = Path(args.project_root)

    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = project_root / manifest

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    rows = read_jsonl(manifest)

    items = []
    failed = []

    for row in rows:
        sample_id = row.get("sample_id", "unknown")
        try:
            audio_path = resolve_audio_path(row, project_root)
            metrics = compute_speech_edge_metrics(audio_path)
            items.append({
                "sample_id": sample_id,
                "audio_path": str(audio_path),
                "preprocessing_version": row.get("preprocessing_version", "original"),
                "metrics": metrics,
            })
        except Exception as e:
            failed.append({
                "sample_id": sample_id,
                "error": str(e),
            })

    output = {
        "manifest": str(manifest),
        "summary": summarize(items),
        "items": items,
        "failed": failed,
    }

    write_json(output_dir / "padding_aware_audio_quality_report.json", output)
    write_jsonl(
        output_dir / "speech_edge_loss_risk_samples.jsonl",
        [x for x in items if x["metrics"]["speech_edge_loss_risk"]],
    )

    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()