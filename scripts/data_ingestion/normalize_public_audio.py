import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path("/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant")
DATA_ROOT = PROJECT_ROOT / "data"

BRONZE_PUBLIC = DATA_ROOT / "data_lake" / "bronze" / "public"
SILVER_AUDIO = DATA_ROOT / "data_lake" / "silver" / "audio_clean"
SILVER_MANIFEST = DATA_ROOT / "data_lake" / "silver" / "asr_manifests" / "asr_silver_manifest_v0_1.jsonl"

DATASETS = ["vietmed", "common_voice_vi", "fosd"]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path):
    if not path.exists():
        return []
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


def ffmpeg_normalize(raw_path: Path, clean_path: Path):
    clean_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(raw_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-af",
        "loudnorm",
        str(clean_path),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ffprobe_duration(path: Path) -> float | None:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    try:
        return round(float(result.stdout.strip()), 3)
    except ValueError:
        return None


def main():
    existing_silver = {}
    if SILVER_MANIFEST.exists():
        for row in read_jsonl(SILVER_MANIFEST):
            existing_silver[row["sample_id"]] = row

    silver_rows = []

    for dataset_name in DATASETS:
        manifest_path = BRONZE_PUBLIC / dataset_name / "metadata" / "manifest_raw.jsonl"
        rows = read_jsonl(manifest_path)

        if not rows:
            print(f"[SKIP] No manifest found for {dataset_name}: {manifest_path}")
            continue

        for row in rows:
            sample_id = row["sample_id"]
            raw_audio_path = PROJECT_ROOT / row["raw_audio_path"]

            clean_audio_name = f"{sample_id}_audio_clean_v0.wav"
            clean_audio_path = SILVER_AUDIO / clean_audio_name

            if sample_id in existing_silver and clean_audio_path.exists():
                silver_rows.append(existing_silver[sample_id])
                print(f"[SKIP] {sample_id} already processed -> {clean_audio_path.name}")
                continue

            try:
                ffmpeg_normalize(raw_audio_path, clean_audio_path)
                clean_checksum = sha256_file(clean_audio_path)
                duration = ffprobe_duration(clean_audio_path)
            except Exception as e:
                print(f"[FAIL] {sample_id}: {e}")
                continue

            silver_row = {
                **row,
                "bronze_audio_path": row["raw_audio_path"],
                "clean_audio_path": str(clean_audio_path.relative_to(PROJECT_ROOT)),
                "sample_rate_hz": 16000,
                "channels": 1,
                "audio_format": "wav",
                "duration_seconds": duration,
                "clean_audio_checksum_sha256": clean_checksum,
                "normalization": {
                    "mono": True,
                    "sample_rate_hz": 16000,
                    "volume_normalized": True,
                    "tool": "ffmpeg_loudnorm"
                },
                "silver_created_at": now_iso(),
                "silver_version": "v0.1.0"
            }

            silver_rows.append(silver_row)
            print(f"[OK] {sample_id} -> {clean_audio_path.name}")

    write_jsonl(SILVER_MANIFEST, silver_rows)
    print(f"[DONE] wrote {len(silver_rows)} rows to {SILVER_MANIFEST}")


if __name__ == "__main__":
    main()