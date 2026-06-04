import json
import argparse
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    manifest = Path(args.manifest)
    rows = read_jsonl(manifest)

    missing_audio = []
    missing_text = []
    split_roles = {}
    train_allowed_count = 0

    for row in rows:
        split_roles[row.get("split_role", "unknown")] = split_roles.get(row.get("split_role", "unknown"), 0) + 1

        audio_path = PROJECT_ROOT / row["clean_audio_path"]
        if not audio_path.exists():
            missing_audio.append(row["sample_id"])

        text = row.get("transcript_text", "")
        if not text.strip():
            missing_text.append(row["sample_id"])

        if row.get("train_allowed") is True:
            train_allowed_count += 1

    print("Manifest:", manifest)
    print("Rows:", len(rows))
    print("Split roles:", split_roles)
    print("Missing audio:", len(missing_audio))
    print("Missing transcript:", len(missing_text))
    print("train_allowed_count:", train_allowed_count)

    if missing_audio:
        print("Example missing audio:", missing_audio[:5])
    if missing_text:
        print("Example missing transcript:", missing_text[:5])


if __name__ == "__main__":
    main()