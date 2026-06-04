import json
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"

INPUT_MANIFEST = DATA_ROOT / "data_lake" / "silver" / "asr_manifests" / "asr_silver_manifest_v0_1.jsonl"

SPLIT_DIR = DATA_ROOT / "data_lake" / "silver" / "asr_manifests" / "splits"
EVAL_DIR = DATA_ROOT / "data_lake" / "evaluation" / "asr_eval_v0_1"

SEED = 42


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def can_train(row: dict) -> bool:
    """
    Chỉ cho phép train khi license/governance đã clear.
    Train candidate có thể tồn tại, nhưng train_allowed có thể false.
    """
    license_status = row.get("license_status")
    governance_status = row.get("governance_status")
    allowed_use = row.get("allowed_use", [])

    return (
        license_status in ["clear", "internal"]
        and governance_status in ["approved_internal", "legal_approved"]
        and "training" in allowed_use
    )


def split_dataset(rows, source_name):
    dataset_rows = [
        r for r in rows
        if r.get("source_name", "").lower() == source_name.lower()
    ]

    random.Random(SEED).shuffle(dataset_rows)

    n = len(dataset_rows)

    if n == 0:
        return [], [], [], "empty"

    # Case 1: Smoke subset nhỏ, ví dụ 50 mẫu
    if n < 100:
        test_size = max(5, int(n * 0.2))
        dev_size = max(5, int(n * 0.2))

        test = dataset_rows[:test_size]
        dev = dataset_rows[test_size:test_size + dev_size]
        train = dataset_rows[test_size + dev_size:]

        split_mode = "smoke_split"

    # Case 2: Benchmark subset vừa, ví dụ 100–999 mẫu
    elif n < 1000:
        test_size = max(50, int(n * 0.2))
        dev_size = max(30, int(n * 0.1))

        test = dataset_rows[:test_size]
        dev = dataset_rows[test_size:test_size + dev_size]
        train = dataset_rows[test_size + dev_size:]

        split_mode = "benchmark_subset_split"

    # Case 3: Dataset lớn/full
    else:
        test_size = 200
        dev_size = 200

        test = dataset_rows[:test_size]
        dev = dataset_rows[test_size:test_size + dev_size]
        train = dataset_rows[test_size + dev_size:]

        split_mode = "full_dataset_split"

    for row in test:
        row["split_mode"] = split_mode
        row["split_role"] = "test_holdout"
        row["train_allowed"] = False
        row["allowed_use"] = ["holdout_only"]
        row["is_holdout"] = True

    for row in dev:
        row["split_mode"] = split_mode
        row["split_role"] = "dev_candidate"
        row["train_allowed"] = False
        row["is_holdout"] = False

        # Dev không dùng train, nhưng dùng chọn model/checkpoint
        if "holdout_only" in row.get("allowed_use", []):
            row["allowed_use"] = ["evaluation", "reference_only"]

    for row in train:
        row["split_mode"] = split_mode
        row["split_role"] = "train_candidate"
        row["is_holdout"] = False
        row["train_allowed"] = can_train(row)

        # Nếu chưa clear governance, giữ làm candidate nhưng không train thật
        if not row["train_allowed"]:
            row["allowed_use"] = ["evaluation", "reference_only"]

    return train, dev, test, split_mode


def main():
    rows = read_jsonl(INPUT_MANIFEST)

    source_names = set(r.get("source_name", "").lower() for r in rows if r.get("source_name"))

    for source_name in source_names:
        train, dev, test, split_mode = split_dataset(rows, source_name)
        
        if split_mode == "empty":
            continue

        write_jsonl(SPLIT_DIR / f"{source_name}_train_candidate_v0_1.jsonl", train)
        write_jsonl(SPLIT_DIR / f"{source_name}_dev_v0_1.jsonl", dev)
        write_jsonl(EVAL_DIR / f"{source_name}_test_holdout_v0_1.jsonl", test)

        print(f"\n--- {source_name.upper()} ---")
        print("Split mode:", split_mode)
        print("train_candidate:", len(train))
        print("dev:", len(dev))
        print("test_holdout:", len(test))

        if len(train) == 0:
            print("[WARN] train_candidate is empty.")
        if len(dev) == 0:
            print("[WARN] dev set is empty.")
        if len(test) == 0:
            print("[WARN] test_holdout is empty.")

        train_allowed_count = sum(1 for r in train if r.get("train_allowed") is True)
        print("train_allowed:", train_allowed_count)

        if train_allowed_count == 0 and len(train) > 0:
            print(
                "[NOTE] train_candidate exists, but train_allowed = 0. "
                "This is expected if license/governance is not approved yet."
            )


if __name__ == "__main__":
    main()