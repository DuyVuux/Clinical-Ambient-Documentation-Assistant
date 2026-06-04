import json
import argparse
from pathlib import Path

from jiwer import wer, cer

from text_normalization_vi import normalize_for_wer


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = read_jsonl(Path(args.predictions))

    results = []
    refs_raw = []
    hyps_raw = []
    refs_norm = []
    hyps_norm = []

    for row in rows:
        ref = row["reference_text"]
        hyp = row["prediction_text"]

        refs_raw.append(ref)
        hyps_raw.append(hyp)

        refs_norm.append(normalize_for_wer(ref))
        hyps_norm.append(normalize_for_wer(hyp))

        results.append({
            "sample_id": row["sample_id"],
            "reference_text": ref,
            "prediction_text": hyp,
            "reference_text_normalized": normalize_for_wer(ref),
            "prediction_text_normalized": normalize_for_wer(hyp),
            "strict_wer": wer(ref, hyp),
            "normalized_wer": wer(normalize_for_wer(ref), normalize_for_wer(hyp)),
            "strict_cer": cer(ref, hyp),
            "normalized_cer": cer(normalize_for_wer(ref), normalize_for_wer(hyp)),
        })

    summary = {
        "n_samples": len(rows),
        "strict_wer": wer(refs_raw, hyps_raw),
        "normalized_wer": wer(refs_norm, hyps_norm),
        "strict_cer": cer(refs_raw, hyps_raw),
        "normalized_cer": cer(refs_norm, hyps_norm),
        "items": results
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "n_samples": summary["n_samples"],
        "strict_wer": summary["strict_wer"],
        "normalized_wer": summary["normalized_wer"],
        "strict_cer": summary["strict_cer"],
        "normalized_cer": summary["normalized_cer"]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()