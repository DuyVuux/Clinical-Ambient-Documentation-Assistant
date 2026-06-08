import json
import argparse
from pathlib import Path


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--edge_risk_samples", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    edge_rows = read_jsonl(args.edge_risk_samples)
    edge_ids = {r["sample_id"] for r in edge_rows}

    pred_rows = read_jsonl(args.predictions)
    subset = [r for r in pred_rows if r["sample_id"] in edge_ids]

    write_jsonl(args.output, subset)

    print(f"edge risk ids: {len(edge_ids)}")
    print(f"prediction rows: {len(pred_rows)}")
    print(f"subset rows: {len(subset)}")


if __name__ == "__main__":
    main()