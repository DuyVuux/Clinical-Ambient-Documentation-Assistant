#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, json, math, re, shutil, tarfile, time, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from transformers import pipeline

TEXT_KEYS = ["segment_text", "sentence", "reference_text", "transcript_text", "text"]
AUDIO_KEYS = ["audio", "audio_path", "path", "wav_path", "file", "file_path"]
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma"}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                row = json.loads(line)
                row["_line_no"] = line_no
                rows.append(row)
    return rows

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def safe_extract_tar(tar_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_abs = dest_dir.resolve()
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            target = (dest_dir / member.name).resolve()
            if not str(target).startswith(str(dest_abs)):
                raise RuntimeError(f"Unsafe tar path: {member.name}")
        tar.extractall(dest_dir)

def find_manifest(extract_dir: Path, explicit_manifest: str | None = None) -> Path:
    if explicit_manifest:
        p = Path(explicit_manifest)
        q = p if p.is_absolute() else extract_dir / explicit_manifest
        if q.exists():
            return q
        raise FileNotFoundError(f"Explicit manifest not found: {explicit_manifest}")
    files = sorted(extract_dir.rglob("*.jsonl"))
    if not files:
        raise FileNotFoundError(f"No JSONL manifest found under {extract_dir}")
    preferred = [p for p in files if any(k in p.name.lower() for k in ["manifest", "run0", "eval", "vimedcss"])]
    return preferred[0] if preferred else files[0]

def pick_reference(row: dict[str, Any]) -> tuple[str, str | None]:
    for key in TEXT_KEYS:
        v = row.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip(), key
    return "", None

def audio_value_to_path_like(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip() or None
    if isinstance(v, dict):
        for k in ["path", "file", "filename"]:
            if v.get(k):
                return str(v[k]).strip()
    return None

def build_basename_index(extract_dir: Path) -> dict[str, Path]:
    return {p.name: p for p in extract_dir.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS}

def resolve_audio_path(row: dict[str, Any], extract_dir: Path, manifest_dir: Path, basename_index: dict[str, Path]):
    for key in AUDIO_KEYS:
        raw = audio_value_to_path_like(row.get(key))
        if not raw:
            continue
        p = Path(raw)
        candidates = [p] if p.is_absolute() else [manifest_dir / p, extract_dir / p, extract_dir / p.name]
        for c in candidates:
            if c.exists() and c.is_file():
                return c, key, raw
        if p.name in basename_index:
            return basename_index[p.name], key, raw
    return None, None, None

def ws(text: str) -> str:
    return " ".join(text.strip().split())

def norm(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[^\w\sÀ-ỹà-ỹ]", " ", text, flags=re.UNICODE).replace("_", " ")
    return ws(text)

def edit_distance(a: list[Any], b: list[Any]) -> int:
    prev = list(range(len(b) + 1))
    cur = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur[0] = i
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev, cur = cur, prev
    return prev[len(b)]

def compute_wer(refs: list[str], hyps: list[str], normalized: bool = False):
    edits, total = 0, 0
    for ref, hyp in zip(refs, hyps):
        ref = norm(ref) if normalized else ws(ref)
        hyp = norm(hyp) if normalized else ws(hyp)
        r, h = ref.split(), hyp.split()
        edits += edit_distance(r, h)
        total += len(r)
    return None if total == 0 else edits / total

def compute_cer(refs: list[str], hyps: list[str], normalized: bool = False):
    edits, total = 0, 0
    for ref, hyp in zip(refs, hyps):
        ref = norm(ref) if normalized else ws(ref)
        hyp = norm(hyp) if normalized else ws(hyp)
        edits += edit_distance(list(ref), list(hyp))
        total += len(ref)
    return None if total == 0 else edits / total

def to_float(v: Any):
    try:
        if v is None or isinstance(v, bool):
            return None
        x = float(v)
        return None if math.isnan(x) or math.isinf(x) else x
    except Exception:
        return None

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--work_dir", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output_predictions", required=True)
    ap.add_argument("--output_metrics", required=True)
    ap.add_argument("--manifest_inside_archive", default=None)
    ap.add_argument("--language", default="vi")
    ap.add_argument("--task", default="transcribe")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--max_samples", type=int, default=None)
    ap.add_argument("--clean_work_dir", action="store_true")
    ap.add_argument("--eval_name", default=None)
    ap.add_argument("--model_label", default=None)
    args = ap.parse_args()

    archive = Path(args.archive)
    work_dir = Path(args.work_dir)
    out_pred = Path(args.output_predictions)
    out_metrics = Path(args.output_metrics)
    if not archive.exists():
        raise FileNotFoundError(f"Archive not found: {archive}")
    if args.clean_work_dir and work_dir.exists():
        shutil.rmtree(work_dir)
    extract_dir = work_dir / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    print(f"[INFO] Extracting: {archive}")
    safe_extract_tar(archive, extract_dir)
    manifest = find_manifest(extract_dir, args.manifest_inside_archive)
    print(f"[INFO] Manifest: {manifest}")

    rows = read_jsonl(manifest)
    if args.max_samples is not None:
        rows = rows[:args.max_samples]
    basename_index = build_basename_index(extract_dir)

    prepared, skipped = [], []
    for row in rows:
        ref, ref_key = pick_reference(row)
        audio, audio_key, audio_raw = resolve_audio_path(row, extract_dir, manifest.parent, basename_index)
        sid = row.get("segment_id") or row.get("sample_id") or f"line_{row.get('_line_no')}"
        reasons = []
        if not ref:
            reasons.append("missing_reference_text")
        if audio is None:
            reasons.append("audio_not_resolved")
        if reasons:
            skipped.append({"segment_id": sid, "line_no": row.get("_line_no"), "reasons": reasons, "audio_key": audio_key, "audio_raw": audio_raw, "ref_key": ref_key})
        else:
            prepared.append({"segment_id": sid, "row": row, "audio": audio, "reference_text": ref, "ref_key": ref_key, "audio_key": audio_key, "audio_raw": audio_raw})
    if not prepared:
        raise RuntimeError("No valid samples prepared for evaluation.")

    if args.device == "auto":
        device = 0 if torch.cuda.is_available() else -1
    elif args.device == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but unavailable.")
        device = 0
    else:
        device = -1
    model_label = args.model_label or str(args.model)
    eval_name = args.eval_name or archive.stem.replace(".tar", "")

    print(f"[INFO] Loading ASR pipeline: {args.model}")
    asr = pipeline("automatic-speech-recognition", model=args.model, tokenizer=args.model, feature_extractor=args.model, device=device)

    preds, refs, hyps = [], [], []
    start = time.time()
    for i, item in enumerate(prepared, start=1):
        sample_t0 = time.time()
        err = None
        try:
            out = asr(str(item["audio"]), generate_kwargs={"language": args.language, "task": args.task})
            hyp = out.get("text", "") if isinstance(out, dict) else str(out)
        except Exception as exc:
            hyp = ""
            err = str(exc)
        runtime = time.time() - sample_t0
        row = item["row"]
        ref = item["reference_text"]
        refs.append(ref)
        hyps.append(hyp)
        preds.append({
            "segment_id": item["segment_id"],
            "sample_id": row.get("sample_id") or item["segment_id"],
            "eval_name": eval_name,
            "model_label": model_label,
            "model": str(args.model),
            "archive": str(archive),
            "audio": str(item["audio"]),
            "reference_text": ref,
            "prediction_text": hyp,
            "runtime_seconds": round(runtime, 4),
            "error": err,
            "duration_seconds": row.get("duration_seconds"),
            "topic": row.get("topic"),
            "cs_terms_count": row.get("cs_terms_count"),
            "cs_terms_list": row.get("cs_terms_list"),
            "original_video_link": row.get("original_video_link"),
            "original_video_title": row.get("original_video_title"),
            "start_time": row.get("start_time"),
            "end_time": row.get("end_time"),
        })
        if i % 10 == 0 or i == len(prepared):
            print(f"[INFO] processed {i}/{len(prepared)}")

    total_runtime = time.time() - start
    durations = [to_float(p.get("duration_seconds")) for p in preds]
    durations = [d for d in durations if d is not None]
    metrics = {
        "created_at": now_iso(),
        "phase": "phase3_run0_baseline",
        "eval_name": eval_name,
        "model": str(args.model),
        "model_label": model_label,
        "archive": str(archive),
        "manifest": str(manifest),
        "n_manifest_rows": len(rows),
        "n_prepared": len(prepared),
        "n_skipped": len(skipped),
        "skipped_preview": skipped[:100],
        "strict_wer": compute_wer(refs, hyps, normalized=False),
        "strict_cer": compute_cer(refs, hyps, normalized=False),
        "normalized_wer": compute_wer(refs, hyps, normalized=True),
        "normalized_cer": compute_cer(refs, hyps, normalized=True),
        "total_runtime_seconds": round(total_runtime, 4),
        "runtime_seconds_per_sample": round(total_runtime / len(prepared), 4),
        "total_audio_hours": round(sum(durations) / 3600, 4) if durations else None,
        "language": args.language,
        "task": args.task,
        "effective_device": device,
        "max_samples": args.max_samples,
        "does_not_train": True,
    }
    write_jsonl(out_pred, preds)
    write_json(out_metrics, metrics)
    print(json.dumps({"status": "DONE", "eval_name": eval_name, "n_prepared": len(prepared), "n_skipped": len(skipped), "strict_wer": metrics["strict_wer"], "strict_cer": metrics["strict_cer"], "normalized_wer": metrics["normalized_wer"], "normalized_cer": metrics["normalized_cer"], "predictions": str(out_pred), "metrics": str(out_metrics)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
