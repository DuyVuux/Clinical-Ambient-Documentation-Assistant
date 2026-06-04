import csv
import sys
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Increase CSV field size limit for Common Voice TSV files.
# Some metadata fields can be larger than Python's default csv limit.
max_csv_field_size = sys.maxsize
while True:
    try:
        csv.field_size_limit(max_csv_field_size)
        break
    except OverflowError:
        max_csv_field_size = int(max_csv_field_size / 10)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"

CV_ROOT = DATA_ROOT / "data_lake" / "bronze" / "public" / "common_voice_vi"
RAW_DOWNLOAD_ROOT = CV_ROOT / "raw_download"
BRONZE_RAW_ROOT = CV_ROOT / "raw"
METADATA_ROOT = CV_ROOT / "metadata"
CHECKSUM_ROOT = CV_ROOT / "checksums"
LICENSE_ROOT = CV_ROOT / "license_snapshot"

SILVER_AUDIO_ROOT = DATA_ROOT / "data_lake" / "silver" / "audio_clean" / "common_voice_vi"
SILVER_MANIFEST_ROOT = DATA_ROOT / "data_lake" / "silver" / "asr_manifests"

VERSION = "v0.1.0"
CREATED_BY = "Duy"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            yield row


def ffmpeg_convert_to_wav(input_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_path),
    ]

    subprocess.run(cmd, check=True)


def get_audio_duration_seconds(path: Path) -> float | None:
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

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return round(float(result.stdout.strip()), 3)
    except Exception:
        return None


def find_cv_vi_dir() -> Path:
    candidates = list(RAW_DOWNLOAD_ROOT.glob("**/vi"))
    for candidate in candidates:
        if (candidate / "clips").exists() and (candidate / "train.tsv").exists():
            return candidate

    raise FileNotFoundError(
        "Không tìm thấy thư mục Common Voice vi. "
        "Hãy giải nén để có dạng raw_download/.../vi/clips và train.tsv/dev.tsv/test.tsv"
    )


def write_license_snapshot():
    LICENSE_ROOT.mkdir(parents=True, exist_ok=True)

    text = f"""# License Snapshot — Common Voice vi

Source: Mozilla Data Collective — Common Voice Scripted Speech Vietnamese
Release used: cv-corpus-25.0-2026-03-09, language vi
License status for MVP registry: clear
License: CC0-1.0 according to Mozilla Data Collective datasheet
Allowed use in this MVP: training, evaluation, reference_only
Governance status: approved_internal for local MVP use

Important constraints:
- Do not attempt to determine the identity of speakers.
- Do not re-host or re-share this dataset.
- Do not commit raw audio to Git.
- Do not upload raw audio to public storage.
- Use as auxiliary ASR robustness data, not as clinical Gold data.

Created at: {now_iso()}
Created by: {CREATED_BY}
Version: {VERSION}
"""
    (LICENSE_ROOT / "LICENSE_SNAPSHOT.md").write_text(text, encoding="utf-8")


def process_split(cv_vi_dir: Path, split_name: str):
    tsv_path = cv_vi_dir / f"{split_name}.tsv"
    clips_dir = cv_vi_dir / "clips"

    if not tsv_path.exists():
        raise FileNotFoundError(f"Không tìm thấy {tsv_path}")

    bronze_split_dir = BRONZE_RAW_ROOT / split_name
    silver_split_dir = SILVER_AUDIO_ROOT / split_name

    bronze_split_dir.mkdir(parents=True, exist_ok=True)
    silver_split_dir.mkdir(parents=True, exist_ok=True)
    METADATA_ROOT.mkdir(parents=True, exist_ok=True)
    CHECKSUM_ROOT.mkdir(parents=True, exist_ok=True)
    SILVER_MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    checksum_lines = []

    for index, row in enumerate(read_tsv(tsv_path), start=1):
        original_path_value = row.get("path") or row.get("clip_path")
        sentence = (row.get("sentence") or "").strip()

        if not original_path_value or not sentence:
            continue

        source_clip_path = clips_dir / original_path_value
        if not source_clip_path.exists():
            print(f"[SKIP] Missing clip: {source_clip_path}")
            continue

        sample_id = f"public_common_voice_vi_{split_name}_{index:06d}"

        raw_audio_ext = source_clip_path.suffix.lower()
        bronze_audio_path = bronze_split_dir / f"{sample_id}{raw_audio_ext}"
        bronze_text_path = bronze_split_dir / f"{sample_id}.txt"
        silver_audio_path = silver_split_dir / f"{sample_id}_audio_clean_v0.wav"

        shutil.copy2(source_clip_path, bronze_audio_path)
        bronze_text_path.write_text(sentence, encoding="utf-8")

        try:
            ffmpeg_convert_to_wav(bronze_audio_path, silver_audio_path)
        except subprocess.CalledProcessError:
            print(f"[SKIP] ffmpeg failed: {bronze_audio_path}")
            continue

        raw_audio_checksum = sha256_file(bronze_audio_path)
        raw_text_checksum = sha256_file(bronze_text_path)
        clean_audio_checksum = sha256_file(silver_audio_path)
        duration_seconds = get_audio_duration_seconds(silver_audio_path)

        if split_name == "train":
            split_role = "auxiliary_train"
            train_allowed = True
        elif split_name == "dev":
            split_role = "auxiliary_dev"
            train_allowed = False
        elif split_name == "test":
            split_role = "auxiliary_test"
            train_allowed = False
        else:
            split_role = "reference_only"
            train_allowed = False

        manifest_row = {
            "sample_id": sample_id,
            "dataset_id": "asr_common_voice_vi_001",
            "source_name": "Common Voice vi",
            "source_type": "public",
            "domain": "general_speech",
            "split_name": split_name,
            "split_role": split_role,
            "raw_audio_path": str(bronze_audio_path.relative_to(PROJECT_ROOT)),
            "raw_transcript_path": str(bronze_text_path.relative_to(PROJECT_ROOT)),
            "clean_audio_path": str(silver_audio_path.relative_to(PROJECT_ROOT)),
            "transcript_text": sentence,
            "language": "vi-VN",
            "duration_seconds": duration_seconds,
            "sample_rate_hz": 16000,
            "channels": 1,
            "raw_audio_checksum_sha256": raw_audio_checksum,
            "raw_text_checksum_sha256": raw_text_checksum,
            "clean_audio_checksum_sha256": clean_audio_checksum,
            "license_status": "clear",
            "allowed_use": ["training", "evaluation", "reference_only"],
            "target_zone": ["bronze", "silver"],
            "contains_phi": "unknown",
            "consent_status": "not_applicable",
            "governance_status": "approved_internal",
            "commercial_pilot_status": "needs_review",
            "wer_eval_allowed": split_name in ["dev", "test"],
            "train_allowed": train_allowed,
            "speaker_id": "not_used",
            "speaker_role": "unknown",
            "speaker_identity_policy": "client_id_not_used_no_speaker_identification",
            "created_at": now_iso(),
            "created_by": CREATED_BY,
            "version": VERSION,
            "notes": (
                "Auxiliary Vietnamese ASR robustness data. "
                "Not clinical Gold. Do not attempt speaker identification. "
                "Do not re-host or re-share dataset."
            ),
        }

        manifest_rows.append(manifest_row)
        checksum_lines.append(f"{raw_audio_checksum}  {bronze_audio_path}")
        checksum_lines.append(f"{raw_text_checksum}  {bronze_text_path}")
        checksum_lines.append(f"{clean_audio_checksum}  {silver_audio_path}")

    manifest_path = SILVER_MANIFEST_ROOT / f"common_voice_vi_{split_name}_manifest_v0_1.jsonl"
    with manifest_path.open("w", encoding="utf-8") as f:
        for item in manifest_rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    checksum_path = CHECKSUM_ROOT / f"common_voice_vi_{split_name}_checksums.sha256"
    checksum_path.write_text("\n".join(checksum_lines), encoding="utf-8")

    print(f"[DONE] {split_name}: {len(manifest_rows)} samples")
    print(f"Manifest: {manifest_path}")


def write_dataset_metadata():
    metadata = {
        "schema_version": "2020-12",
        "dataset_id": "asr_common_voice_vi_001",
        "source_name": "Common Voice vi",
        "source_type": "public",
        "setting": "other",
        "specialty": "general_speech",
        "language": "vi-VN",
        "audio_path": "data/data_lake/bronze/public/common_voice_vi/raw",
        "transcript_path": "data/data_lake/bronze/public/common_voice_vi/raw",
        "contains_phi": "unknown",
        "consent_status": "not_applicable",
        "license_status": "clear",
        "allowed_use": ["training", "evaluation", "reference_only"],
        "review_status": "raw",
        "version": VERSION,
        "governance_status": "approved_internal",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "created_by": CREATED_BY,
        "owner": CREATED_BY,
        "retention_policy": "keep_versioned",
        "access_control_policy": "local_owner_only",
        "audit_log_required": True,
        "is_holdout": False,
        "commercial_pilot_status": "needs_review",
        "target_zone": ["bronze", "silver"],
        "data_sensitivity": "moderate",
        "source_uri": "Mozilla Data Collective Common Voice Scripted Speech Vietnamese",
        "license_snapshot_path": "data/data_lake/bronze/public/common_voice_vi/license_snapshot/LICENSE_SNAPSHOT.md",
        "provenance": {
            "origin": "Mozilla Data Collective",
            "collection_method": "public_download",
            "annotation_method": "none",
            "notes": (
                "Official Common Voice vi dataset. Use only as auxiliary ASR robustness data. "
                "Not a clinical dataset. Not Gold. Do not attempt speaker identification."
            ),
        },
    }

    path = METADATA_ROOT / "dataset_metadata.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] dataset metadata: {path}")


def main():
    write_license_snapshot()
    cv_vi_dir = find_cv_vi_dir()

    if len(sys.argv) > 1:
        splits = sys.argv[1:]
    else:
        splits = ["train", "dev", "test"]

    allowed_splits = {"train", "dev", "test"}

    for split_name in splits:
        if split_name not in allowed_splits:
            raise ValueError(
                f"Invalid split '{split_name}'. Allowed splits: {sorted(allowed_splits)}"
            )

        process_split(cv_vi_dir, split_name)

    write_dataset_metadata()


if __name__ == "__main__":
    main()