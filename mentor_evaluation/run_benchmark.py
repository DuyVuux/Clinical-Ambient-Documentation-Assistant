#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mentor Test Benchmark Run Script
Tiêu chuẩn hóa quy trình đánh giá mô hình ASR cho dự án Clinical Ambient Documentation Assistant.
Chạy độc lập, không làm ảnh hưởng đến cấu trúc mã nguồn có sẵn.
"""

import argparse
import sys
import platform
import importlib.util
import time
import json
import re
import csv
import unicodedata
import tarfile
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Optional, Tuple, FrozenSet

# Kiểm tra thư viện bắt buộc
required_packages = ["torch", "transformers", "soundfile", "tqdm"]
missing = [pkg for pkg in required_packages if importlib.util.find_spec(pkg) is None]

if missing:
    print(f"[FAIL] Missing required packages: {missing}")
    print("Vui lòng cài đặt trước khi chạy lệnh: pip install torch transformers soundfile tqdm pandas")
    sys.exit(1)

import torch
from transformers import pipeline
import soundfile as sf

# --- KHÔNG TỰ TÍNH METRICS MÀ SẼ IMPORT TỪ CỦA SẾP ---
import sys
from pathlib import Path

# Thêm đường dẫn thư mục gốc dự án vào sys.path để có thể import scripts/asr_vimedcss/asr_benchmark.py
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from scripts.asr_vimedcss import asr_benchmark



# --- INFERENCE UTILS ---
def clean_tsv_cell(s: Any) -> str:
    s = str(s if s is not None else "").replace("\t", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()

def read_transcript_txt(path: Path) -> Dict[str, str]:
    refs: Dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]
    
    tab_lines = [line for line in lines if "\t" in line]
    if tab_lines:
        for line in tab_lines:
            key, text = line.split("\t", 1)
            key = re.sub(r"\s+", " ", key).strip()
            text = clean_tsv_cell(text)
            if key and text: refs[key] = text
        return refs
        
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            key, text = parts
            key = re.sub(r"\s+", " ", key).strip()
            text = clean_tsv_cell(text)
            if key and text: refs[key] = text
    return refs

def key_variants(key: str) -> List[str]:
    raw = str(key).strip().replace("\\", "/")
    p = Path(raw)
    name, stem = p.name, p.stem
    variants = {raw, raw.lower(), name, name.lower(), stem, stem.lower(), f"{stem}.wav", f"{stem.lower()}.wav"}
    return [v for v in variants if v]

def build_audio_index(audio_files: List[Path]) -> Dict[str, Path]:
    index: Dict[str, Path] = {}
    for p in audio_files:
        for k in {p.name, p.name.lower(), p.stem, p.stem.lower()}:
            index.setdefault(k, p)
    return index

def find_audio_for_key(key: str, audio_index: Dict[str, Path]) -> Optional[Path]:
    for v in key_variants(key):
        if v in audio_index: return audio_index[v]
    return None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_manifest(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                row = json.loads(line)
                row["_line_no"] = line_no
                rows.append(row)
    return rows

def load_done_ids(pred_path: Path) -> Set[str]:
    done = set()
    if not pred_path.exists(): return done
    with pred_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try: row = json.loads(line)
            except Exception: continue
            sid = row.get("sample_id")
            if sid: done.add(str(sid))
    return done

def export_prediction_tsv(pred_jsonl: Path, pred_tsv: Path) -> int:
    n = 0
    pred_tsv.parent.mkdir(parents=True, exist_ok=True)
    with pred_jsonl.open("r", encoding="utf-8", errors="replace") as f, pred_tsv.open("w", encoding="utf-8") as out:
        for line in f:
            if not line.strip(): continue
            row = json.loads(line)
            sid = clean_tsv_cell(row.get("sample_id") or row.get("audio_basename") or f"sample_{n:06d}")
            hyp = clean_tsv_cell(row.get("prediction_text", ""))
            out.write(f"{sid}\t{hyp}\n")
            n += 1
    return n

def build_asr_pipeline(model_path: str):
    use_cuda = torch.cuda.is_available()
    device = 0 if use_cuda else -1
    kwargs = {"model": model_path, "tokenizer": model_path, "feature_extractor": model_path, "device": device}
    if use_cuda: kwargs["torch_dtype"] = torch.float16
    print(f"\n[INFO] Đang tải mô hình ASR: {model_path}")
    print(f"[INFO] Thiết bị: {'GPU' if use_cuda else 'CPU'}")
    return pipeline("automatic-speech-recognition", **kwargs)

def run_asr_inference(manifest: Path, model_path: str, output_predictions: Path, output_prediction_tsv: Path, output_metrics: Path, max_samples: Optional[int] = None, resume: bool = True, log_every: int = 5, language: str = "vi", task: str = "transcribe", model_label: Optional[str] = None):
    rows = read_manifest(manifest)
    if max_samples is not None: rows = rows[:max_samples]
    if not rows: raise RuntimeError("Manifest rỗng, không có dữ liệu để chạy inference.")
    
    output_predictions.parent.mkdir(parents=True, exist_ok=True)
    output_metrics.parent.mkdir(parents=True, exist_ok=True)
    
    done_ids = load_done_ids(output_predictions) if resume else set()
    mode = "a" if resume and output_predictions.exists() else "w"
    
    print("\n=== BẮT ĐẦU INFERENCE ===")
    print(f"- Số mẫu trong manifest: {len(rows)}")
    print(f"- Số mẫu đã hoàn thành trước đó: {len(done_ids)}")
    print(f"- Tiếp tục (resume): {resume}")
    
    asr = build_asr_pipeline(model_path)
    started = time.time()
    n_new = 0; n_error = 0; runtimes = []
    
    with output_predictions.open(mode, encoding="utf-8") as out:
        for idx, row in enumerate(rows, start=1):
            sid = str(row.get("sample_id") or row.get("audio_basename") or f"sample_{idx:06d}")
            if sid in done_ids: continue
            
            audio = row.get("audio")
            ref = row.get("reference_text", "")
            t0 = time.time(); err = None; hyp = ""
            
            try:
                result = asr(str(audio), generate_kwargs={"language": language, "task": task})
                hyp = result.get("text", "") if isinstance(result, dict) else str(result)
            except Exception as exc:
                err = repr(exc)
                n_error += 1
                
            runtime = time.time() - t0
            runtimes.append(runtime)
            n_new += 1
            
            pred_row = {
                "sample_id": sid, "audio": audio, "reference_text": ref, "prediction_text": hyp, 
                "model": model_path, "model_label": model_label or model_path, 
                "runtime_seconds": round(runtime, 4), "error": err, 
                "original_ref_key": row.get("original_ref_key"), "created_at": now_iso()
            }
            out.write(json.dumps(pred_row, ensure_ascii=False) + "\n")
            out.flush()
            
            if n_new == 1 or n_new % log_every == 0 or idx == len(rows):
                elapsed = time.time() - started
                avg = elapsed / max(n_new, 1)
                remaining = max(len(rows) - idx, 0)
                eta = remaining * avg
                print("-" * 60, flush=True)
                print(f"[Tiến độ] Đã chạy mới: {n_new} | Dòng: {idx}/{len(rows)} | T/g: {elapsed:.1f}s | Tốc độ: {avg:.2f}s/mẫu | ETA: {eta/60:.1f}phút", flush=True)
                print(f"[Mẫu] {sid} | Lỗi: {err}", flush=True)
                print(f"[REF] {str(ref)[:150]}", flush=True)
                print(f"[HYP] {str(hyp)[:150]}", flush=True)
                
    n_tsv = export_prediction_tsv(output_predictions, output_prediction_tsv)
    total_runtime = time.time() - started
    
    metrics = {
        "created_at": now_iso(), "manifest": str(manifest), "model": model_path, 
        "model_label": model_label or model_path, "n_manifest_rows": len(rows), 
        "n_newly_processed": n_new, "n_prediction_tsv_rows": n_tsv, "n_errors_new": n_error, 
        "resume": resume, "cuda_available": torch.cuda.is_available(), 
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, 
        "total_runtime_seconds": round(total_runtime, 4), 
        "mean_runtime_seconds_per_new_sample": round(sum(runtimes) / len(runtimes), 4) if runtimes else None, 
        "predictions_jsonl": str(output_predictions), "prediction_tsv": str(output_prediction_tsv)
    }
    output_metrics.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


# --- MAIN PIPELINE ---
def main():
    parser = argparse.ArgumentParser(description="Chạy Benchmark ASR Model (Mentor Evaluation)")
    parser.add_argument("--testset-dir", type=str, required=True, help="Đường dẫn đến thư mục chứa transcript.txt và thư mục audio/")
    parser.add_argument("--model-path", type=str, required=True, help="Đường dẫn đến model (local path hoặc HuggingFace ID)")
    parser.add_argument("--output-dir", type=str, default="mentor_evaluation_outputs", help="Thư mục xuất kết quả")
    parser.add_argument("--run-label", type=str, default="benchmark_run", help="Tên phiên chạy để tạo thư mục con (VD: week5_run)")
    parser.add_argument("--smoke-test", action="store_true", help="Chỉ chạy thử với 3 mẫu đầu tiên")
    parser.add_argument("--no-resume", action="store_true", help="Tắt chế độ resume, ghi đè lại kết quả từ đầu")
    parser.add_argument("--viet-syllables-path", type=str, default=None, help="Đường dẫn file syllables tiếng việt để tính CS-WER")
    parser.add_argument("--language", type=str, default="vi", help="Ngôn ngữ ASR")
    parser.add_argument("--task", type=str, default="transcribe", help="Task của ASR (transcribe/translate)")
    
    args = parser.parse_args()

    TESTSET_ROOT = Path(args.testset_dir).expanduser().resolve()
    AUDIO_DIR = TESTSET_ROOT / "audio"
    TRANSCRIPT_PATH = TESTSET_ROOT / "transcript.txt"
    OUTPUT_ROOT = Path(args.output_dir).expanduser().resolve()
    RUN_DIR = OUTPUT_ROOT / args.run_label

    REF_DIR = RUN_DIR / "reference"
    PRED_DIR = RUN_DIR / "predictions"
    REPORT_DIR = RUN_DIR / "reports"
    
    for d in [OUTPUT_ROOT, RUN_DIR, REF_DIR, PRED_DIR, REPORT_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CLINICAL AMBIENT DOCUMENTATION ASSISTANT - MENTOR BENCHMARK")
    print("=" * 60)
    print(f"Testset Dir : {TESTSET_ROOT}")
    print(f"Model Path  : {args.model_path}")
    print(f"Output Dir  : {RUN_DIR}")
    
    # --- PHASE 1: PREPARE DATA ---
    print("\n[1/4] Chuẩn hóa thư mục đầu vào...")
    if not TESTSET_ROOT.exists(): sys.exit(f"[LỖI] Thư mục Testset không tồn tại: {TESTSET_ROOT}")
    if not AUDIO_DIR.exists(): sys.exit(f"[LỖI] Không tìm thấy thư mục con 'audio' trong {TESTSET_ROOT}")
    if not TRANSCRIPT_PATH.exists(): sys.exit(f"[LỖI] Không tìm thấy 'transcript.txt' trong {TESTSET_ROOT}")
    
    audio_files = sorted(AUDIO_DIR.glob("*.wav"))
    refs = read_transcript_txt(TRANSCRIPT_PATH)
    audio_index = build_audio_index(audio_files)
    
    matched_rows, unmatched_refs = [], []
    used_audio = set()
    for ref_key, text in refs.items():
        audio_path = find_audio_for_key(ref_key, audio_index)
        if audio_path is None:
            unmatched_refs.append({"ref_key": ref_key, "text": text})
            continue
        used_audio.add(str(audio_path.resolve()))
        matched_rows.append({
            "sample_id": audio_path.name,
            "audio": str(audio_path.resolve()),
            "reference_text": text,
            "original_ref_key": ref_key,
            "audio_basename": audio_path.name,
            "audio_stem": audio_path.stem,
        })
    
    if not matched_rows:
        sys.exit("[LỖI] Không khớp được audio nào với transcript. Vui lòng kiểm tra lại file transcript.txt")

    manifest_path = REF_DIR / "manifest.jsonl"
    reference_tsv_path = REF_DIR / "reference.tsv"
    summary_path = REF_DIR / "prepare_summary.json"
    
    with manifest_path.open("w", encoding="utf-8") as f:
        for row in matched_rows: f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with reference_tsv_path.open("w", encoding="utf-8") as f:
        for row in matched_rows: f.write(f"{clean_tsv_cell(row['sample_id'])}\t{clean_tsv_cell(row['reference_text'])}\n")
    
    prep = {
        "n_audio_files": len(audio_files), "n_transcript_rows": len(refs),
        "n_matched": len(matched_rows), "n_unmatched_refs": len(unmatched_refs)
    }
    summary_path.write_text(json.dumps(prep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> Chuẩn bị thành công {len(matched_rows)} audio có nhãn text.")

    # --- PHASE 2: INFERENCE ---
    print("\n[2/4] Bắt đầu Inference (Chạy model)...")
    pred_jsonl = PRED_DIR / "predictions.jsonl"
    pred_tsv = PRED_DIR / "prediction.tsv"
    infer_metrics = PRED_DIR / "inference_metrics.json"
    
    inf = run_asr_inference(
        manifest=manifest_path,
        model_path=args.model_path,
        output_predictions=pred_jsonl,
        output_prediction_tsv=pred_tsv,
        output_metrics=infer_metrics,
        max_samples=3 if args.smoke_test else None,
        resume=not args.no_resume,
        language=args.language,
        task=args.task,
        model_label=args.run_label
    )

    # --- PHASE 3: EVALUATION ---
    print("\n[3/4] Chạy đánh giá Metrics (Dùng công cụ chuẩn của sếp: asr_benchmark.py)...")
    
    # Sử dụng hàm load_file và compute_metrics từ script của sếp
    references = asr_benchmark.load_file(str(reference_tsv_path))
    predictions = asr_benchmark.load_file(str(pred_tsv))
    
    viet_syllables_path = args.viet_syllables_path
    if not viet_syllables_path:
        # Tự động tìm trong thư mục dự án
        default_syllables = project_root / "scripts" / "asr_vimedcss" / "viet_syllables.txt"
        if default_syllables.exists():
            viet_syllables_path = str(default_syllables)
            print(f"[INFO] Tự động nạp danh sách từ điển tiếng Việt: {viet_syllables_path}")

    viet_set = None
    if viet_syllables_path:
        viet_set = asr_benchmark.load_viet_syllables(str(viet_syllables_path))
        
    metrics_obj = asr_benchmark.compute_metrics(references, predictions, viet_set)
    
    # Chuyển đổi Dataclass thành dict để lưu báo cáo
    m_dict = {
        "wer": metrics_obj.wer,
        "cer": metrics_obj.cer,
        "substitutions": metrics_obj.substitutions,
        "deletions": metrics_obj.deletions,
        "insertions": metrics_obj.insertions,
        "ref_words": metrics_obj.ref_words,
        "ref_chars": metrics_obj.ref_chars,
        "matched": metrics_obj.matched,
        "total_ref": metrics_obj.total_ref,
        "total_hyp": metrics_obj.total_hyp,
        "cs_wer": metrics_obj.cs_wer,
        "n_wer": metrics_obj.n_wer,
        "negation_miss_rate": metrics_obj.negation_miss_rate,
        "negation_missed": metrics_obj.negation_missed,
        "negation_ref_count": metrics_obj.negation_ref_count
    }
    
    benchmark_output = {
        "created_at": now_iso(), "run_label": args.run_label, "model": args.model_path,
        "metrics": m_dict
    }
    
    benchmark_metrics_path = REPORT_DIR / "benchmark_metrics.json"
    benchmark_metrics_path.write_text(json.dumps(benchmark_output, ensure_ascii=False, indent=2), encoding="utf-8")

    def fmt_pct(x): return "N/A" if x is None else f"{x * 100:.2f}%"

    print("\n" + "=" * 60)
    print("KẾT QUẢ ĐÁNH GIÁ (asr_benchmark.py)")
    print("=" * 60)
    print(f"Files matched      : {metrics_obj.matched}")
    print(f"WER                : {fmt_pct(metrics_obj.wer)}")
    print(f"CER                : {fmt_pct(metrics_obj.cer)}")
    if metrics_obj.cs_wer is not None:
        print(f"CS-WER             : {fmt_pct(metrics_obj.cs_wer)}")
    print(f"Negation miss rate : {fmt_pct(metrics_obj.negation_miss_rate)}")
    print("=" * 60)

    # --- PHASE 4: REPORT & BUNDLE ---
    print("\n[4/4] Lưu báo cáo và xuất Artifacts...")
    report_path = REPORT_DIR / "BENCHMARK_REPORT.md"
    
    report_md = f"""# Báo cáo Benchmark - Clinical ASR 

## 1. Thông tin cấu hình
- Testset : `{TESTSET_ROOT}`
- Model   : `{args.model_path}`
- Phiên chạy: `{args.run_label}`

## 2. Thống kê dữ liệu
- File Audio `.wav`: {prep['n_audio_files']}
- Số dòng Transcript: {prep['n_transcript_rows']}
- Khớp thành công: {metrics_obj.matched} / {metrics_obj.total_ref} (Số liệu để đánh giá)

## 3. Kết quả đánh giá tổng quan (bằng công cụ `asr_benchmark.py`)
| Metric | Giá trị | Ý nghĩa |
|---|---|---|
| **WER** | **{fmt_pct(metrics_obj.wer)}** | Tỉ lệ lỗi từ - Chỉ số tổng quát ASR |
| **CER** | **{fmt_pct(metrics_obj.cer)}** | Tỉ lệ lỗi ký tự |
| CS-WER | {fmt_pct(metrics_obj.cs_wer)} | Tỉ lệ lỗi trên từ mượn ngoại lai |
| N-WER | {fmt_pct(metrics_obj.n_wer)} | Tỉ lệ lỗi trên từ tiếng Việt thuần |
| Phủ định (Miss) | {fmt_pct(metrics_obj.negation_miss_rate)} | Tỉ lệ bỏ sót các từ "không", "chưa" |

## 4. Chi tiết Lỗi (Breakdown)
### 4.1. Lỗi Từ (Word Errors)
- Tổng số từ tham chiếu (Reference words): **{metrics_obj.ref_words}**
- Tổng số lỗi: **{metrics_obj.substitutions + metrics_obj.deletions + metrics_obj.insertions}**
  - Nhận diện sai (Substitutions): {metrics_obj.substitutions}
  - Bỏ sót từ (Deletions): {metrics_obj.deletions}
  - Nhận diện thừa (Insertions): {metrics_obj.insertions}

### 4.2. Từ Phủ Định (Negation Words)
- Số từ phủ định tham chiếu: **{metrics_obj.negation_ref_count}** (trong {metrics_obj.negation_utterances} câu)
- Số từ phủ định bị bỏ sót (Missed): **{metrics_obj.negation_missed}**
"""

    if metrics_obj.cs_wer is not None:
        report_md += f"""
### 4.3. Từ Mượn / Thuật Ngữ Y Khoa (Code-Switching)
- Tổng số từ ngoại lai (CS ref words): **{metrics_obj.cs_ref_words}**
- Tổng số lỗi: **{metrics_obj.cs_substitutions + metrics_obj.cs_deletions + metrics_obj.cs_insertions}**
  - Nhận diện sai (Substitutions): {metrics_obj.cs_substitutions}
  - Bỏ sót từ (Deletions): {metrics_obj.cs_deletions}
  - Nhận diện thừa (Insertions): {metrics_obj.cs_insertions}

### 4.4. Từ Tiếng Việt Thuần (Native Vietnamese)
- Tổng số từ tiếng Việt: **{metrics_obj.n_ref_words}**
- Tổng số lỗi: **{metrics_obj.n_substitutions + metrics_obj.n_deletions + metrics_obj.n_insertions}**
  - Nhận diện sai (Substitutions): {metrics_obj.n_substitutions}
  - Bỏ sót từ (Deletions): {metrics_obj.n_deletions}
  - Nhận diện thừa (Insertions): {metrics_obj.n_insertions}
"""

    report_md += f"""
## 5. Chi tiết chạy (Inference)
- Số mẫu đã xử lý: {inf.get('n_newly_processed')}
- Thiết bị chạy: {inf.get('gpu') or 'CPU'}
- Tổng thời gian: {inf.get('total_runtime_seconds')} giây
- Trung bình: {inf.get('mean_runtime_seconds_per_new_sample')} giây/mẫu

## 6. Dữ liệu đầu ra (Outputs)
- Báo cáo định dạng JSON: `{benchmark_metrics_path.name}`
- Dự đoán gốc: `{pred_jsonl.name}`
"""

    report_path.write_text(report_md, encoding="utf-8")
    
    # Bundle TAR
    bundle_path = OUTPUT_ROOT / f"{args.run_label}_artifacts.tar.gz"
    files_to_include = [manifest_path, reference_tsv_path, summary_path, pred_jsonl, pred_tsv, infer_metrics, benchmark_metrics_path, report_path]
    
    with tarfile.open(bundle_path, "w:gz") as tar:
        for p in files_to_include:
            if p.exists(): tar.add(p, arcname=str(p.relative_to(RUN_DIR)))
            
    print(f"Đã xuất báo cáo tại: {report_path}")
    print(f"Đã nén toàn bộ kết quả vào: {bundle_path}")
    print("\nHOÀN THÀNH!")

if __name__ == "__main__":
    main()
