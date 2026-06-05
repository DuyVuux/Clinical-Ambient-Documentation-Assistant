import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Any


DEFAULT_TERM_GROUPS = {
    "negation": [
        "không",
        "chưa",
        "phủ nhận",
        "không ghi nhận",
        "chưa từng",
        "không có"
    ],
    "symptom": [
        "ho",
        "sốt",
        "đau ngực",
        "khó thở",
        "đau bụng",
        "tiêu chảy",
        "đau đầu",
        "mất ngủ",
        "rát họng",
        "buồn nôn",
        "nôn",
        "chóng mặt",
        "mệt mỏi"
    ],
    "medication": [
        "paracetamol",
        "amoxicillin",
        "amlodipine",
        "insulin",
        "omeprazole",
        "ibuprofen",
        "metformin"
    ],
    "allergy": [
        "dị ứng",
        "dị ứng thuốc",
        "dị ứng penicillin",
        "dị ứng hải sản",
        "chưa từng dị ứng thuốc",
        "không dị ứng thuốc"
    ],
    "dose_unit": [
        "mg",
        "miligam",
        "ml",
        "viên",
        "gói",
        "lần",
        "ngày",
        "mỗi ngày",
        "mỗi sáng",
        "mỗi tối"
    ],
    "number": [
        "37.8",
        "37 độ 8",
        "ba mươi bảy độ tám",
        "500",
        "năm trăm",
        "3 ngày",
        "ba ngày",
        "một viên",
        "hai viên"
    ],
    "red_flag": [
        "đau ngực",
        "khó thở",
        "sốt cao",
        "spo2",
        "nôn ra máu",
        "đi ngoài ra máu",
        "lú lẫn",
        "yếu liệt"
    ]
}


PUNCT_PATTERN = r"[\,\.\!\?\:\;\(\)\[\]\{\}\"“”‘’…]"


def normalize_basic(text: str) -> str:
    if text is None:
        return ""

    text = unicodedata.normalize("NFC", str(text))
    text = text.lower().strip()

    replacements = {
        "năm trăm miligam": "500 mg",
        "năm trăm mi li gam": "500 mg",
        "năm trăm mg": "500 mg",
        "ba mươi bảy độ tám": "37.8 độ",
        "ba mươi bảy phẩy tám": "37.8",
        "ba ngày": "3 ngày",
        "một viên": "1 viên",
        "hai viên": "2 viên",
        "sp o2": "spo2",
        "s p o 2": "spo2"
    }

    for src, tgt in replacements.items():
        text = text.replace(src, tgt)

    text = re.sub(PUNCT_PATTERN, " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no} in {path}: {exc}") from exc

    return rows


def load_terms(path: Path | None) -> Dict[str, List[str]]:
    if path is None:
        return DEFAULT_TERM_GROUPS

    if not path.exists():
        raise FileNotFoundError(f"Term file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Term file must be a JSON object: group_name -> list of terms")

    cleaned = {}

    for group, terms in data.items():
        if not isinstance(terms, list):
            raise ValueError(f"Term group '{group}' must be a list")

        cleaned[group] = [str(t).strip() for t in terms if str(t).strip()]

    return cleaned


def find_terms(text: str, terms: List[str]) -> List[str]:
    found = []

    normalized_text = normalize_basic(text)

    for term in terms:
        normalized_term = normalize_basic(term)

        if not normalized_term:
            continue

        if normalized_term in normalized_text:
            found.append(term)

    return sorted(set(found))


def severity_for_group(group: str) -> str:
    if group in {"negation", "allergy"}:
        return "critical"
    if group in {"medication", "dose_unit", "red_flag"}:
        return "high"
    if group in {"number", "symptom"}:
        return "moderate"
    return "low"


def analyze_item(row: Dict[str, Any], term_groups: Dict[str, List[str]]) -> Dict[str, Any]:
    ref_raw = row.get("reference_text", "")
    pred_raw = row.get("prediction_text", "")

    ref_norm = normalize_basic(ref_raw)
    pred_norm = normalize_basic(pred_raw)

    group_errors = {}

    for group, terms in term_groups.items():
        ref_terms = find_terms(ref_norm, terms)
        pred_terms = find_terms(pred_norm, terms)

        missing_terms = [term for term in ref_terms if normalize_basic(term) not in [normalize_basic(x) for x in pred_terms]]
        inserted_terms = [term for term in pred_terms if normalize_basic(term) not in [normalize_basic(x) for x in ref_terms]]

        group_errors[group] = {
            "severity": severity_for_group(group),
            "reference_terms": ref_terms,
            "prediction_terms": pred_terms,
            "missing_terms": missing_terms,
            "inserted_terms": inserted_terms,
            "has_reference_terms": len(ref_terms) > 0,
            "has_missing_terms": len(missing_terms) > 0,
            "has_inserted_terms": len(inserted_terms) > 0
        }

    critical_flags = []

    for group, detail in group_errors.items():
        if detail["severity"] in {"critical", "high"} and detail["has_missing_terms"]:
            critical_flags.append({
                "group": group,
                "severity": detail["severity"],
                "missing_terms": detail["missing_terms"]
            })

    return {
        "sample_id": row.get("sample_id"),
        "model_name": row.get("model_name"),
        "source_name": row.get("source_name"),
        "split_role": row.get("split_role"),
        "clean_audio_path": row.get("clean_audio_path"),
        "reference_text": ref_raw,
        "prediction_text": pred_raw,
        "reference_normalized": ref_norm,
        "prediction_normalized": pred_norm,
        "group_errors": group_errors,
        "critical_flags": critical_flags,
        "has_critical_or_high_missing_error": len(critical_flags) > 0
    }


def summarize(items: List[Dict[str, Any]], term_groups: Dict[str, List[str]]) -> Dict[str, Any]:
    summary = {
        "n_samples": len(items),
        "n_samples_with_critical_or_high_missing_error": 0,
        "groups": {}
    }

    for group in term_groups:
        summary["groups"][group] = {
            "severity": severity_for_group(group),
            "samples_with_reference_terms": 0,
            "samples_with_missing_terms": 0,
            "samples_with_inserted_terms": 0,
            "missing_terms_total": 0,
            "inserted_terms_total": 0,
            "top_missing_terms": {},
            "top_inserted_terms": {}
        }

    for item in items:
        if item["has_critical_or_high_missing_error"]:
            summary["n_samples_with_critical_or_high_missing_error"] += 1

        for group, detail in item["group_errors"].items():
            group_summary = summary["groups"][group]

            if detail["has_reference_terms"]:
                group_summary["samples_with_reference_terms"] += 1

            if detail["has_missing_terms"]:
                group_summary["samples_with_missing_terms"] += 1

            if detail["has_inserted_terms"]:
                group_summary["samples_with_inserted_terms"] += 1

            group_summary["missing_terms_total"] += len(detail["missing_terms"])
            group_summary["inserted_terms_total"] += len(detail["inserted_terms"])

            for term in detail["missing_terms"]:
                key = normalize_basic(term)
                group_summary["top_missing_terms"][key] = group_summary["top_missing_terms"].get(key, 0) + 1

            for term in detail["inserted_terms"]:
                key = normalize_basic(term)
                group_summary["top_inserted_terms"][key] = group_summary["top_inserted_terms"].get(key, 0) + 1

    for group in summary["groups"]:
        group_summary = summary["groups"][group]
        group_summary["top_missing_terms"] = sorted(
            group_summary["top_missing_terms"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        group_summary["top_inserted_terms"] = sorted(
            group_summary["top_inserted_terms"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

    return summary


def write_markdown_report(path: Path, result: Dict[str, Any]) -> None:
    summary = result["summary"]
    model_name = result.get("model_name", "unknown_model")

    lines = []
    lines.append(f"# ASR Medical Error Analysis — {model_name}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Samples: {summary['n_samples']}")
    lines.append(f"- Samples with critical/high missing error: {summary['n_samples_with_critical_or_high_missing_error']}")
    lines.append("")
    lines.append("## Group summary")
    lines.append("")
    lines.append("| Group | Severity | Ref samples | Missing samples | Missing total | Inserted samples | Inserted total |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    for group, detail in summary["groups"].items():
        lines.append(
            f"| {group} | {detail['severity']} | "
            f"{detail['samples_with_reference_terms']} | "
            f"{detail['samples_with_missing_terms']} | "
            f"{detail['missing_terms_total']} | "
            f"{detail['samples_with_inserted_terms']} | "
            f"{detail['inserted_terms_total']} |"
        )

    lines.append("")
    lines.append("## Top missing terms")
    lines.append("")

    for group, detail in summary["groups"].items():
        lines.append(f"### {group}")
        if not detail["top_missing_terms"]:
            lines.append("- None")
        else:
            for term, count in detail["top_missing_terms"]:
                lines.append(f"- `{term}`: {count}")
        lines.append("")

    lines.append("## Critical/high examples")
    lines.append("")

    examples = [
        item for item in result["items"]
        if item["has_critical_or_high_missing_error"]
    ][:20]

    if not examples:
        lines.append("No critical/high missing examples found.")
    else:
        for item in examples:
            lines.append(f"### {item.get('sample_id')}")
            lines.append("")
            lines.append(f"**Reference:** {item.get('reference_text', '')}")
            lines.append("")
            lines.append(f"**Prediction:** {item.get('prediction_text', '')}")
            lines.append("")
            lines.append("**Flags:**")
            for flag in item["critical_flags"]:
                lines.append(f"- {flag['group']} ({flag['severity']}): missing {flag['missing_terms']}")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze clinically important ASR errors from prediction JSONL."
    )
    parser.add_argument("--predictions", required=True, help="Prediction JSONL with reference_text and prediction_text")
    parser.add_argument("--output", required=True, help="Output JSON report path")
    parser.add_argument("--terms", default=None, help="Optional JSON term groups file")
    parser.add_argument("--markdown", default=None, help="Optional Markdown report path")

    args = parser.parse_args()

    prediction_path = Path(args.predictions)
    output_path = Path(args.output)
    terms_path = Path(args.terms) if args.terms else None
    markdown_path = Path(args.markdown) if args.markdown else None

    rows = load_jsonl(prediction_path)
    term_groups = load_terms(terms_path)

    items = [analyze_item(row, term_groups) for row in rows]
    summary = summarize(items, term_groups)

    model_name = "unknown_model"
    if rows:
        model_name = rows[0].get("model_name", "unknown_model")

    result = {
        "model_name": model_name,
        "prediction_file": str(prediction_path),
        "term_groups": term_groups,
        "summary": summary,
        "items": items
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if markdown_path:
        write_markdown_report(markdown_path, result)

    print(json.dumps({
        "model_name": model_name,
        "n_samples": summary["n_samples"],
        "n_samples_with_critical_or_high_missing_error": summary["n_samples_with_critical_or_high_missing_error"],
        "groups": summary["groups"]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
