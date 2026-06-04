import argparse
import json
import os
from pathlib import Path

# Thư mục gốc của dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Từ khóa phủ định (Negation)
NEGATION_WORDS = ['không', 'chưa', 'chẳng', 'đừng', 'khỏi', 'hết', 'vô', 'phi', 'kém']

# Từ khóa Y khoa và Thuốc (Medical terms & Medications - MVP List)
MEDICAL_KEYWORDS = [
    'thuốc', 'paracetamol', 'huyết áp', 'tiểu đường', 'đái tháo đường', 'suy tim', 
    'ung thư', 'viêm', 'sốt', 'đau', 'khám', 'bệnh viện', 'bác sĩ', 'dị ứng', 
    'mỡ máu', 'cholesterol', 'xét nghiệm', 'siêu âm', 'x-quang', 'mri', 'ct', 
    'chuẩn đoán', 'chẩn đoán', 'triệu chứng', 'điều trị', 'phẫu thuật', 'mổ', 
    'nhịp tim', 'hô hấp', 'hen suyễn', 'máu', 'glucose', 'insulin'
]

def analyze_errors(metrics_path: Path):
    with open(metrics_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    items = data.get('items', [])
    if not items:
        print(f"Warning: No items found in {metrics_path}")
        return None
        
    report = {
        'total_samples': len(items),
        'negation_missed': [],      # Model missed a negation
        'negation_hallucinated': [],# Model added a negation
        'medical_missed': [],       # Model missed a medical term
        'medical_hallucinated': [], # Model hallucinated a medical term
        'hallucination_loop': []    # Model got stuck in a loop (e.g. repetition)
    }
    
    for idx, item in enumerate(items):
        # Sử dụng bản normalized để so sánh chính xác hơn
        ref = item.get('reference_text_normalized', item.get('reference_text', '')).lower()
        pred = item.get('prediction_text_normalized', item.get('prediction_text', '')).lower()
        audio_path = item.get('sample_id', f'sample_{idx}')
        
        # Tokenize đơn giản
        ref_tokens = set(ref.split())
        pred_tokens = set(pred.split())
        
        # --- 1. Phân tích Phủ định (Negations) ---
        for neg in NEGATION_WORDS:
            # So sánh từ đơn
            if neg in ref_tokens and neg not in pred_tokens:
                report['negation_missed'].append({'audio': audio_path, 'term': neg, 'ref': ref, 'pred': pred})
            if neg not in ref_tokens and neg in pred_tokens:
                report['negation_hallucinated'].append({'audio': audio_path, 'term': neg, 'ref': ref, 'pred': pred})
                
        # --- 2. Phân tích Y khoa (Medical Terms) ---
        for med in MEDICAL_KEYWORDS:
            # So sánh theo cụm từ (med có thể có khoảng trắng)
            if med in ref and med not in pred:
                report['medical_missed'].append({'audio': audio_path, 'term': med, 'ref': ref, 'pred': pred})
            if med not in ref and med in pred:
                report['medical_hallucinated'].append({'audio': audio_path, 'term': med, 'ref': ref, 'pred': pred})
                
        # --- 3. Phát hiện Ảo giác Lặp từ (Repetition Hallucination) ---
        # Nếu prediction dài hơn reference 3 lần và số từ > 10
        if len(pred_tokens) > len(ref_tokens) * 3 and len(pred_tokens) > 10:
            # Kiểm tra lặp từ
            words = pred.split()
            if len(words) > 0:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.3: # Lặp từ quá nhiều
                    report['hallucination_loop'].append({'audio': audio_path, 'ref': ref, 'pred': pred})

    return report

def main():
    parser = argparse.ArgumentParser(description="Clinical Error Analysis for ASR")
    parser.add_argument("--metrics_dir", type=str, default="experiments/asr/baseline/metrics/dev", help="Directory containing _metrics.json files")
    parser.add_argument("--output", type=str, default="experiments/asr/baseline/clinical_error_report_dev.md", help="Output markdown report file")
    
    args = parser.parse_args()
    
    metrics_dir = PROJECT_ROOT / args.metrics_dir
    output_file = PROJECT_ROOT / args.output
    
    if not metrics_dir.exists():
        raise FileNotFoundError(f"Metrics directory not found: {metrics_dir}")
        
    models = ['phowhisper_base', 'phowhisper_medium', 'whisper_small']
    all_reports = {}
    
    for model in models:
        metrics_file = metrics_dir / f"{model}_dev_metrics.json"
        if metrics_file.exists():
            print(f"Analyzing {model}...")
            all_reports[model] = analyze_errors(metrics_file)
        else:
            print(f"File not found: {metrics_file}")
            
    # Xây dựng báo cáo Markdown
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Báo cáo Phân tích Lỗi Y Khoa (Clinical Error Analysis)\n\n")
        out.write("Báo cáo này phân tích các lỗi nghiêm trọng trong y tế: bỏ sót/tự thêm từ phủ định, từ khóa y khoa, và lỗi ảo giác lặp từ.\n\n")
        
        for model, rep in all_reports.items():
            if not rep: continue
            
            out.write(f"## Mô hình: `{model}`\n")
            out.write(f"- **Tổng số mẫu:** {rep['total_samples']}\n")
            out.write(f"- **Bỏ sót Phủ định (Missed Negation):** {len(rep['negation_missed'])} lỗi\n")
            out.write(f"- **Ảo giác Phủ định (Hallucinated Negation):** {len(rep['negation_hallucinated'])} lỗi\n")
            out.write(f"- **Bỏ sót Từ khóa Y khoa (Missed Medical Term):** {len(rep['medical_missed'])} lỗi\n")
            out.write(f"- **Ảo giác Từ khóa Y khoa (Hallucinated Medical Term):** {len(rep['medical_hallucinated'])} lỗi\n")
            out.write(f"- **Ảo giác lặp từ (Loop Hallucination):** {len(rep['hallucination_loop'])} lỗi\n\n")
            
            # Liệt kê chi tiết một vài lỗi phủ định nguy hiểm
            if rep['negation_missed'] or rep['negation_hallucinated']:
                out.write("### Cảnh báo: Lỗi Phủ định (Nguy hiểm)\n")
                out.write("| Loại | Từ khóa | Reference | Prediction |\n")
                out.write("|---|---|---|---|\n")
                # Hiển thị tối đa 5 lỗi mỗi loại
                for err in rep['negation_missed'][:5]:
                    out.write(f"| Bỏ sót | `{err['term']}` | {err['ref']} | {err['pred']} |\n")
                for err in rep['negation_hallucinated'][:5]:
                    out.write(f"| Tự thêm | `{err['term']}` | {err['ref']} | {err['pred']} |\n")
                out.write("\n")
                
            # Liệt kê chi tiết lặp từ
            if rep['hallucination_loop']:
                out.write("### Cảnh báo: Lỗi Lặp từ (Hallucination Loop)\n")
                out.write("| Reference | Prediction |\n")
                out.write("|---|---|\n")
                for err in rep['hallucination_loop'][:3]: # Hiển thị 3 lỗi lặp từ
                    out.write(f"| {err['ref']} | {err['pred'][:100]}... (bị cắt bớt) |\n")
                out.write("\n")
                
            out.write("---\n\n")
            
    print(f"\nPhân tích hoàn tất! Báo cáo đã được lưu tại: {output_file}")

if __name__ == "__main__":
    main()
