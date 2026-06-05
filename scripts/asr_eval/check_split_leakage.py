import json
import argparse
from pathlib import Path


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def get_ids(rows):
    return {row["sample_id"] for row in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--dev", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    train = read_jsonl(Path(args.train))
    dev = read_jsonl(Path(args.dev))
    test = read_jsonl(Path(args.test))

    train_ids = get_ids(train)
    dev_ids = get_ids(dev)
    test_ids = get_ids(test)

    train_dev_overlap = sorted(train_ids & dev_ids)
    train_test_overlap = sorted(train_ids & test_ids)
    dev_test_overlap = sorted(dev_ids & test_ids)

    report = {
        "counts": {
            "train": len(train),
            "dev": len(dev),
            "test": len(test)
        },
        "overlap_counts": {
            "train_dev": len(train_dev_overlap),
            "train_test": len(train_test_overlap),
            "dev_test": len(dev_test_overlap)
        },
        "overlaps": {
            "train_dev": train_dev_overlap[:20],
            "train_test": train_test_overlap[:20],
            "dev_test": dev_test_overlap[:20]
        },
        "status": "PASS" if not train_dev_overlap and not train_test_overlap and not dev_test_overlap else "FAIL"
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()