#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 — ViMedCSS manifest engineering and subset materialization.

Creates run manifests and optional .tar.gz subset archives for:
- Run 0 baseline eval sets
- Run A smoke train/eval sets
- Run B mini adaptation train/eval sets
- Run C balanced strategic train/eval sets
- VietMed dev small forgetting eval set

This script does NOT train, does NOT create Run D in Phase 2, and does NOT
train on validation/test/hard.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import shutil
import tarfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPLITS = ["train", "validation", "test", "hard"]
EN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+\-/.]*")
WS_RE = re.compile(r"\s+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sfloat(x: Any) -> float | None:
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        if math.isnan(float(x)) or math.isinf(float(x)):
            return None
        return float(x)
    if isinstance(x, str):
        x = x.strip().replace(",", ".")
        if not x:
            return None
        try:
            out = float(x)
            if math.isnan(out) or math.isinf(out):
                return None
            return out
        except ValueError:
            return None
    return None


def sint(x: Any) -> int | None:
    f = sfloat(x)
    return int(f) if f is not None else None


def clean_text(x: Any) -> str:
    if x is None:
        return ""
    if not isinstance(x, str):
        x = str(x)
    return WS_RE.sub(" ", x.strip())


def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def english_count(text: str) -> int:
    return len(EN_RE.findall(text))


def parse_cs_terms(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(v).strip() for v in x if str(v).strip()]
    if isinstance(x, str):
        v = x.strip()
        if not v:
            return []
        try:
            obj = json.loads(v)
            if isinstance(obj, list):
                return [str(t).strip() for t in obj if str(t).strip()]
        except Exception:
            pass
        return [p.strip() for p in re.split(r"[,;|]", v) if p.strip()]
    return [str(x).strip()] if str(x).strip() else []


def stable_int(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def safe_name(x: str) -> str:
    x = re.sub(r"[^A-Za-z0-9_.\-]+", "_", x)
    return x[:120] if x else "sample"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSONL manifest: {path}")
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {e}") from e
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                fields.append(k)
                seen.add(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def detect_manifest(vroot: Path, split: str) -> Path:
    new = vroot / "manifests" / "raw" / f"vimedcss_{split}_raw.jsonl"
    old = vroot / "manifests" / f"vimedcss_{split}_raw.jsonl"
    return new if new.exists() else old


def load_suspects(vroot: Path) -> set[str]:
    path = vroot / "data_audit" / "vimedcss_suspect_samples.csv"
    if not path.exists():
        return set()
    out = set()
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            sid = r.get("segment_id") or r.get("sample_id")
            if sid:
                out.add(str(sid).strip())
    return out


def audio_ref(row: dict[str, Any]) -> tuple[str | None, str | None]:
    a = row.get("audio")
    if isinstance(a, str) and a.strip():
        return a.strip(), "audio"
    if isinstance(a, dict):
        for k in ["path", "filepath", "file", "filename"]:
            v = a.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip(), f"audio.{k}"
        if a.get("bytes") is not None:
            return None, "audio.bytes"
    for k in ["audio_path", "path", "file_path", "wav_path"]:
        v = row.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip(), k
    return None, None


def resolve_audio(ref: str | None, roots: list[Path]) -> Path | None:
    if not ref:
        return None
    p = Path(ref)
    if p.is_absolute() and p.exists():
        return p
    for root in roots:
        cand = root / ref
        if cand.exists():
            return cand
    basename = p.name
    if basename != ref:
        for root in roots:
            cand = root / basename
            if cand.exists():
                return cand
    for root in roots:
        for match in root.rglob(basename):
            if match.is_file():
                return match
    return None


def get_id(row: dict[str, Any], split: str, idx: int) -> str:
    val = row.get("segment_id") or row.get("sample_id") or row.get("id")
    return str(val).strip() if val is not None and str(val).strip() else f"vimedcss_{split}_{idx:06d}"


def make_feat(row: dict[str, Any], split: str, idx: int, suspects: set[str]) -> dict[str, Any]:
    text = clean_text(row.get("segment_text") or row.get("sentence") or row.get("text"))
    cs_terms = parse_cs_terms(row.get("cs_terms_list"))
    cs_count = sint(row.get("cs_terms_count"))
    if cs_count is None:
        cs_count = len(cs_terms)
    ref, field = audio_ref(row)
    sid = get_id(row, split, idx)
    dur = sfloat(row.get("duration_seconds"))
    feat = {
        "split": split,
        "segment_id": sid,
        "segment_text": text,
        "duration_seconds": dur,
        "cs_terms_count": cs_count,
        "cs_terms_list": cs_terms,
        "english_token_count": english_count(text),
        "word_count": word_count(text),
        "topic": clean_text(row.get("topic")) or "unknown",
        "audio_ref": ref,
        "audio_field": field,
        "is_suspect": sid in suspects,
        "source_row": row,
    }
    feat["is_basic_valid"] = bool(
        text and feat["word_count"] > 1 and ref and dur is not None and 1.0 <= dur <= 25.0
    )
    feat["selection_group"] = classify(feat)
    return feat


def classify(f: dict[str, Any]) -> str:
    cs = int(f.get("cs_terms_count") or 0)
    eng = int(f.get("english_token_count") or 0)
    dur = float(f.get("duration_seconds") or 0.0)
    words = int(f.get("word_count") or 0)
    if cs >= 2 or eng >= 2:
        return "high_code_switching"
    if (cs >= 1 or eng >= 1) and 10.0 <= dur <= 25.0 and words >= 4:
        return "moderate_noisy_hard_like"
    return "normal_medical_vietnamese"


def eligible(items: list[dict[str, Any]], exclude_suspect: bool = True) -> list[dict[str, Any]]:
    return [x for x in items if x["is_basic_valid"] and (not exclude_suspect or not x["is_suspect"])]


def shuffle(items: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    items = list(items)
    random.Random(seed).shuffle(items)
    return items


def select_count(items: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    return shuffle(items, seed)[:n]


def select_stratified(items: list[dict[str, Any]], n: int, ratios: dict[str, float], seed: int) -> list[dict[str, Any]]:
    by = defaultdict(list)
    for x in items:
        by[x["selection_group"]].append(x)
    selected, used = [], set()
    for group, ratio in ratios.items():
        target = int(round(n * ratio))
        for x in shuffle(by.get(group, []), seed + stable_int(group))[:target]:
            if x["segment_id"] not in used:
                selected.append(x)
                used.add(x["segment_id"])
    if len(selected) < n:
        for x in shuffle(items, seed + 999):
            if x["segment_id"] not in used:
                selected.append(x)
                used.add(x["segment_id"])
            if len(selected) >= n:
                break
    return selected[:n]


def select_hours(items: list[dict[str, Any]], hours: float, ratios: dict[str, float], seed: int) -> list[dict[str, Any]]:
    target = hours * 3600.0
    by = defaultdict(list)
    for x in items:
        by[x["selection_group"]].append(x)
    selected, used = [], set()

    def dur(rows):
        return sum(float(r.get("duration_seconds") or 0.0) for r in rows)

    for group, ratio in ratios.items():
        group_target = target * ratio
        group_rows = []
        for x in shuffle(by.get(group, []), seed + stable_int(group)):
            if x["segment_id"] in used:
                continue
            group_rows.append(x)
            used.add(x["segment_id"])
            if dur(group_rows) >= group_target:
                break
        selected.extend(group_rows)
    if dur(selected) < target:
        for x in shuffle(items, seed + 1001):
            if x["segment_id"] not in used:
                selected.append(x)
                used.add(x["segment_id"])
            if dur(selected) >= target:
                break
    return selected


def normalize_run_row(f: dict[str, Any], run_name: str, usage: str) -> dict[str, Any]:
    row = f["source_row"]
    resolved = f.get("audio_ref_resolved") or f["audio_ref"]
    return {
        "sample_id": f["segment_id"],
        "segment_id": f["segment_id"],
        "dataset_id": "tensorxt/ViMedCSS",
        "source_name": "ViMedCSS",
        "source_split": f["split"],
        "run_name": run_name,
        "usage": usage,
        "audio": str(resolved),
        "source_audio_field": f["audio_field"],
        "sentence": f["segment_text"],
        "segment_text": f["segment_text"],
        "duration_seconds": f["duration_seconds"],
        "topic": f["topic"],
        "cs_terms_count": f["cs_terms_count"],
        "cs_terms_list": f["cs_terms_list"],
        "english_token_count": f["english_token_count"],
        "word_count": f["word_count"],
        "selection_group": f["selection_group"],
        "original_video_link": row.get("original_video_link"),
        "original_video_title": row.get("original_video_title"),
        "start_time": row.get("start_time"),
        "end_time": row.get("end_time"),
        "language": "vi",
        "task": "transcribe",
        "created_at": now_iso(),
    }


def normalize_vietmed(row: dict[str, Any], idx: int) -> dict[str, Any] | None:
    sid = row.get("sample_id") or row.get("segment_id") or f"vietmed_dev_{idx:06d}"
    text = clean_text(row.get("sentence") or row.get("transcript_text") or row.get("reference_text") or row.get("text") or row.get("segment_text"))
    audio = row.get("audio") or row.get("preprocessed_audio_path") or row.get("clean_audio_path") or row.get("audio_path")
    if not text or not audio:
        return None
    return {
        "sample_id": str(sid), "segment_id": str(sid), "dataset_id": "vietmed", "source_name": "VietMed",
        "source_split": "dev", "run_name": "forgetting_eval", "usage": "forgetting_eval", "audio": audio,
        "sentence": text, "segment_text": text, "duration_seconds": sfloat(row.get("duration_seconds")),
        "topic": row.get("topic") or "vietmed_dev", "cs_terms_count": 0, "cs_terms_list": [],
        "english_token_count": english_count(text), "word_count": word_count(text),
        "selection_group": "vietmed_forgetting_eval", "language": "vi", "task": "transcribe", "created_at": now_iso(),
    }


def make_tar(src_dir: Path, out_tar: Path) -> None:
    out_tar.parent.mkdir(parents=True, exist_ok=True)
    if out_tar.exists():
        out_tar.unlink()
    with tarfile.open(out_tar, "w:gz") as tar:
        tar.add(src_dir, arcname=src_dir.name)


def materialize(subset_name: str, rows: list[dict[str, Any]], manifest_path: Path, vroot: Path, work_root: Path,
                archive_root: Path, drive_archive_root: Path | None, manifests_only: bool, allow_missing_audio: bool,
                audio_roots: list[Path] | None = None) -> dict[str, Any]:
    write_jsonl(manifest_path, rows)
    total_hours = sum(float(r.get("duration_seconds") or 0.0) for r in rows) / 3600.0
    if manifests_only:
        return {"subset_name": subset_name, "rows": len(rows), "total_hours": round(total_hours, 4),
                "manifest_path": str(manifest_path), "local_archive_path": None, "drive_archive_path": None,
                "copied_audio": 0, "missing_audio": None, "mode": "manifests_only"}

    out_dir = work_root / "materialized_subsets" / subset_name
    if out_dir.exists():
        shutil.rmtree(out_dir)
    audio_dir = out_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    roots = build_audio_roots(vroot, audio_roots)
    materialized, copied, missing = [], 0, 0
    for i, row in enumerate(rows):
        r = dict(row)
        src = resolve_audio(str(r.get("audio")) if r.get("audio") is not None else None, roots)
        if src is None:
            missing += 1
            r["audio_materialization_status"] = "missing_source_audio"
            r["materialized_audio"] = None
            if not allow_missing_audio:
                raise FileNotFoundError(
                    f"Missing audio for subset={subset_name}, sample={r.get('sample_id')}, audio={r.get('audio')}. "
                    "Use --manifests_only for local planning, or run on Colab CPU where audio files are materialized."
                )
        else:
            dst = audio_dir / f"{i:06d}_{safe_name(str(r.get('sample_id') or i))}{src.suffix or '.wav'}"
            shutil.copy2(src, dst)
            r["source_audio_original"] = r.get("audio")
            r["audio"] = f"audio/{dst.name}"
            r["materialized_audio"] = r["audio"]
            r["audio_materialization_status"] = "copied"
            copied += 1
        materialized.append(r)
    write_jsonl(out_dir / "manifest.jsonl", materialized)
    write_json(out_dir / "subset_metadata.json", {"subset_name": subset_name, "rows": len(rows), "total_hours": round(total_hours,4), "copied_audio": copied, "missing_audio": missing, "created_at": now_iso()})
    local_tar = archive_root / f"{subset_name}.tar.gz"
    make_tar(out_dir, local_tar)
    drive_tar = None
    if drive_archive_root:
        drive_archive_root.mkdir(parents=True, exist_ok=True)
        drive_tar = drive_archive_root / f"{subset_name}.tar.gz"
        shutil.copy2(local_tar, drive_tar)
    return {"subset_name": subset_name, "rows": len(rows), "total_hours": round(total_hours, 4),
            "manifest_path": str(manifest_path), "local_archive_path": str(local_tar),
            "drive_archive_path": str(drive_tar) if drive_tar else None,
            "copied_audio": copied, "missing_audio": missing, "mode": "materialized_archive"}


def group_counts(rows: list[dict[str, Any]]) -> str:
    return json.dumps(dict(Counter(r.get("selection_group", "unknown") for r in rows)), ensure_ascii=False)


def render_report(index_rows: list[dict[str, Any]], raw_counts: dict[str, int], eligible_counts: dict[str, int], suspect_count: int, args) -> str:
    lines = ["# ViMedCSS Subset Materialization Report", "", "## Objective", "", "Create run manifests and subset archives for ViMedCSS progressive fine-tuning.", "", "## Mode", "", f"- manifests_only: `{args.manifests_only}`", f"- allow_missing_audio: `{args.allow_missing_audio}`", f"- skip_runD: `{args.skip_runD}`", "", "## Raw and eligible counts", "", "| Split | Raw rows | Eligible rows |", "|---|---:|---:|"]
    for s in SPLITS:
        lines.append(f"| {s} | {raw_counts.get(s)} | {eligible_counts.get(s)} |")
    lines += ["", f"- Suspect IDs loaded from Phase 1: `{suspect_count}`", "", "## Generated subsets", "", "| Subset | Rows | Hours | Manifest | Local archive | Drive archive | Copied audio | Missing audio | Mode |", "|---|---:|---:|---|---|---|---:|---:|---|"]
    for r in index_rows:
        lines.append(f"| `{r['subset_name']}` | {r['rows']} | {r['total_hours']} | `{r['manifest_path']}` | `{r['local_archive_path']}` | `{r['drive_archive_path']}` | {r['copied_audio']} | {r['missing_audio']} | {r['mode']} |")
    lines += ["", "## Run C selection policy", "", "| Group | Target ratio | Source split | Purpose |", "|---|---:|---|---|", "| High code-switching | 60–70% | train only | Adapt English medical terms |", "| Normal medical Vietnamese | 20–30% | train only | Preserve Vietnamese medical ASR |", "| Moderate noisy/hard-like | ~10% | train only | Robustness without broken samples |", "", "Hard split is not used for training. Hard-like examples are selected from train split only.", "", "## Guardrails", "", "- No validation/test/hard samples are used for training.", "- Run D is not created in Phase 2.", "- Suspect samples from Phase 1 are excluded by default.", "- Training should not read directly from Drive. Copy archive to `/content`, extract, then train.", "", "## Next phase", "", "Proceed to Phase 3 Run 0 baseline only after the Week 5 checkpoint warning is resolved.", ""]
    return "\n".join(lines)


def find_vietmed_manifest(vroot: Path, explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([
        vroot.parent / "finetune" / "week5" / "data" / "dev_manifest_for_phowhisper.jsonl",
        vroot.parents[3] / "experiments" / "asr" / "finetune" / "week5" / "data" / "dev_manifest_for_phowhisper.jsonl" if len(vroot.parents) > 3 else vroot,
        vroot.parents[3] / "data" / "data_lake" / "silver" / "asr_manifests" / "vietmed_dev_preprocessed_selected_safe_v0_1.jsonl" if len(vroot.parents) > 3 else vroot,
    ])
    for p in candidates:
        if p.is_file():
            return p
    return None


def build_audio_roots(vroot: Path, extra_roots: list[Path] | None = None) -> list[Path]:
    roots = []
    if extra_roots:
        roots.extend(extra_roots)
    project_root = vroot
    for parent in [vroot] + list(vroot.parents):
        if (parent / ".git").exists() or (parent / "data").is_dir():
            project_root = parent
            break
    audio_candidates = [
        project_root / "data" / "vimedcss_audio",
        project_root / "data",
        vroot / "audio",
        vroot / "data",
        vroot,
        project_root,
        Path.cwd(),
    ]
    for cand in audio_candidates:
        if cand.is_dir() and cand not in roots:
            roots.append(cand)
    return roots


def resolve_feats_audio(feats: dict[str, list[dict[str, Any]]], roots: list[Path]) -> None:
    resolved_count = 0
    for split_feats in feats.values():
        for feat in split_feats:
            ref = feat.get("audio_ref")
            if not ref:
                continue
            found = resolve_audio(ref, roots)
            if found:
                feat["audio_ref_resolved"] = str(found.resolve())
                resolved_count += 1
            else:
                feat["audio_ref_resolved"] = ref
    total = sum(len(v) for v in feats.values())
    print(f"[INFO] Audio resolved: {resolved_count}/{total} samples")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vimedcss_root", required=True)
    ap.add_argument("--drive_root", default=None)
    ap.add_argument("--work_root", required=True)
    ap.add_argument("--audio_search_roots", nargs="*", default=None)
    ap.add_argument("--make_run0", action="store_true")
    ap.add_argument("--make_runA", action="store_true")
    ap.add_argument("--make_runB", action="store_true")
    ap.add_argument("--make_runC", action="store_true")
    ap.add_argument("--make_runD", action="store_true")
    ap.add_argument("--skip_runD", action="store_true")
    ap.add_argument("--manifests_only", action="store_true")
    ap.add_argument("--allow_missing_audio", action="store_true")
    ap.add_argument("--skip_forgetting_eval", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--run0_val_n", type=int, default=200)
    ap.add_argument("--run0_hard_n", type=int, default=200)
    ap.add_argument("--run0_test_n", type=int, default=200)
    ap.add_argument("--runA_train_n", type=int, default=200)
    ap.add_argument("--runA_eval_n", type=int, default=100)
    ap.add_argument("--runB_train_n", type=int, default=1000)
    ap.add_argument("--runB_eval_val_n", type=int, default=200)
    ap.add_argument("--runB_eval_hard_n", type=int, default=200)
    ap.add_argument("--runC_train_hours", type=float, default=4.0)
    ap.add_argument("--runC_eval_val_n", type=int, default=200)
    ap.add_argument("--runC_eval_hard_n", type=int, default=200)
    ap.add_argument("--vietmed_dev_manifest", default=None)
    ap.add_argument("--vietmed_dev_small_n", type=int, default=100)
    args = ap.parse_args()

    if args.make_runD and not args.skip_runD:
        raise SystemExit("Run D must not be created in Phase 2. Pass --skip_runD.")

    vroot = Path(args.vimedcss_root)
    work_root = Path(args.work_root)
    archive_root = vroot / "preprocessing" / "subset_archives"
    drive_archive = Path(args.drive_root) / "subset_archives" if args.drive_root else None
    manifests_root = vroot / "manifests"
    suspects = load_suspects(vroot)
    extra_audio_roots = [Path(p) for p in args.audio_search_roots] if args.audio_search_roots else None
    audio_roots = build_audio_roots(vroot, extra_audio_roots)

    raw = {s: read_jsonl(detect_manifest(vroot, s)) for s in SPLITS}
    feats = {s: [make_feat(row, s, i, suspects) for i, row in enumerate(rows)] for s, rows in raw.items()}
    resolve_feats_audio(feats, audio_roots)
    elig = {s: eligible(items) for s, items in feats.items()}

    index_rows = []

    def add_subset(name: str, selected: list[dict[str, Any]], mpath: Path, usage: str, run_name: str):
        rows = [normalize_run_row(f, run_name, usage) for f in selected]
        info = materialize(name, rows, mpath, vroot, work_root, archive_root, drive_archive, args.manifests_only, args.allow_missing_audio, audio_roots)
        info["group_counts"] = group_counts(rows)
        info["created_at"] = now_iso()
        index_rows.append(info)

    if args.make_run0:
        add_subset("run0_eval_val_200", select_count(elig["validation"], min(args.run0_val_n, len(elig["validation"])), args.seed+10), manifests_root/"run0"/"run0_eval_val_200.jsonl", "eval_validation", "run0")
        add_subset("run0_eval_hard_200", select_count(elig["hard"], min(args.run0_hard_n, len(elig["hard"])), args.seed+11), manifests_root/"run0"/"run0_eval_hard_200.jsonl", "eval_hard_reporting", "run0")
        add_subset("run0_eval_test_200", select_count(elig["test"], min(args.run0_test_n, len(elig["test"])), args.seed+12), manifests_root/"run0"/"run0_eval_test_200.jsonl", "eval_test_reporting", "run0")

    if args.make_runA:
        tr = select_stratified(elig["train"], min(args.runA_train_n, len(elig["train"])), {"high_code_switching":0.60, "normal_medical_vietnamese":0.30, "moderate_noisy_hard_like":0.10}, args.seed+20)
        add_subset("runA_train_200", tr, manifests_root/"runA"/"runA_train_200.jsonl", "train", "runA_smoke_200")
        add_subset("runA_eval_val_100", select_count(elig["validation"], min(args.runA_eval_n, len(elig["validation"])), args.seed+21), manifests_root/"runA"/"runA_eval_val_100.jsonl", "eval_validation", "runA_smoke_200")

    if args.make_runB:
        tr = select_stratified(elig["train"], min(args.runB_train_n, len(elig["train"])), {"high_code_switching":0.60, "normal_medical_vietnamese":0.30, "moderate_noisy_hard_like":0.10}, args.seed+30)
        add_subset("runB_train_1000", tr, manifests_root/"runB"/"runB_train_1000.jsonl", "train", "runB_mini_1000")
        add_subset("runB_eval_val_200", select_count(elig["validation"], min(args.runB_eval_val_n, len(elig["validation"])), args.seed+31), manifests_root/"runB"/"runB_eval_val_200.jsonl", "eval_validation", "runB_mini_1000")
        add_subset("runB_eval_hard_200", select_count(elig["hard"], min(args.runB_eval_hard_n, len(elig["hard"])), args.seed+32), manifests_root/"runB"/"runB_eval_hard_200.jsonl", "eval_hard_reporting", "runB_mini_1000")

    if args.make_runC:
        tr = select_hours(elig["train"], args.runC_train_hours, {"high_code_switching":0.65, "normal_medical_vietnamese":0.25, "moderate_noisy_hard_like":0.10}, args.seed+40)
        add_subset("runC_train_4h", tr, manifests_root/"runC"/"runC_train_4h.jsonl", "train", "runC_balanced_4h")
        add_subset("runC_eval_val_200", select_count(elig["validation"], min(args.runC_eval_val_n, len(elig["validation"])), args.seed+41), manifests_root/"runC"/"runC_eval_val_200.jsonl", "eval_validation", "runC_balanced_4h")
        add_subset("runC_eval_hard_200", select_count(elig["hard"], min(args.runC_eval_hard_n, len(elig["hard"])), args.seed+42), manifests_root/"runC"/"runC_eval_hard_200.jsonl", "eval_hard_reporting", "runC_balanced_4h")

    if not args.skip_forgetting_eval:
        vm = find_vietmed_manifest(vroot, args.vietmed_dev_manifest)
        if vm is None:
            print("[WARN] VietMed dev manifest not found. Skipping vietmed_dev_small.")
        else:
            converted = []
            for i, row in enumerate(read_jsonl(vm)):
                out = normalize_vietmed(row, i)
                if out:
                    converted.append(out)
                if len(converted) >= args.vietmed_dev_small_n:
                    break
            if converted:
                info = materialize("vietmed_dev_small", converted, manifests_root/"forgetting_eval"/"vietmed_dev_small.jsonl", vroot, work_root, archive_root, drive_archive, args.manifests_only, args.allow_missing_audio, audio_roots)
                info["group_counts"] = json.dumps({"vietmed_forgetting_eval": len(converted)}, ensure_ascii=False)
                info["created_at"] = now_iso()
                index_rows.append(info)

    write_csv(vroot/"preprocessing"/"subset_index.csv", index_rows)
    raw_counts = {s: len(raw[s]) for s in SPLITS}
    eligible_counts = {s: len(elig[s]) for s in SPLITS}
    (vroot/"preprocessing"/"SUBSET_MATERIALIZATION_REPORT.md").write_text(render_report(index_rows, raw_counts, eligible_counts, len(suspects), args), encoding="utf-8")
    write_json(vroot/"preprocessing"/"subset_materialization_summary.json", {"created_at": now_iso(), "index_rows": index_rows, "raw_counts": raw_counts, "eligible_counts": eligible_counts, "suspect_count": len(suspects), "manifests_only": args.manifests_only})

    print(json.dumps({"status":"DONE", "subsets": len(index_rows), "subset_index": str(vroot/"preprocessing"/"subset_index.csv"), "report": str(vroot/"preprocessing"/"SUBSET_MATERIALIZATION_REPORT.md")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()