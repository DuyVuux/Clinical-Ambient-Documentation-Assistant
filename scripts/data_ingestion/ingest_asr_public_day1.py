import os
import json
import hashlib
import random
from itertools import islice
from pathlib import Path
from datetime import datetime, timezone

import soundfile as sf
from datasets import load_dataset


PROJECT_ROOT = Path("/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant")
DATA_ROOT = PROJECT_ROOT / "data"
BRONZE_ROOT = DATA_ROOT / "data_lake" / "bronze" / "public"

CREATED_BY = "Duy"
VERSION = "v0.1.0"
SEED = 42


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_text(sample):
    for key in ["text", "sentence", "transcription", "transcript", "normalized_text"]:
        value = sample.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def save_audio_from_hf_sample(sample, audio_path: Path):
    audio = sample.get("audio")
    if not audio:
        raise ValueError("Sample has no audio field")

    array = audio["array"]
    sampling_rate = audio["sampling_rate"]

    audio_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(audio_path), array, sampling_rate)

    return sampling_rate


def ingest_hf_streaming_dataset(
    dataset_name: str,
    dataset_config: str | None,
    split: str,
    source_name: str,
    dataset_id: str,
    domain: str,
    output_name: str,
    n_samples: int,
    license_status: str,
    governance_status: str,
    allowed_use: list[str],
    token: str | None = None,
    trust_remote_code: bool = False,
):
    output_root = BRONZE_ROOT / output_name
    raw_dir = output_root / "raw"
    metadata_dir = output_root / "metadata"
    checksum_dir = output_root / "checksums"
    license_dir = output_root / "license_snapshot"

    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    checksum_dir.mkdir(parents=True, exist_ok=True)
    license_dir.mkdir(parents=True, exist_ok=True)

    ds_kwargs = {
        "path": dataset_name,
        "split": split,
        "streaming": True,
        "trust_remote_code": trust_remote_code,
    }

    if dataset_config:
        ds_kwargs["name"] = dataset_config
    if token:
        ds_kwargs["token"] = token

    dataset = load_dataset(**ds_kwargs)

    rows = []
    checksum_lines = []

    for idx, sample in enumerate(islice(dataset, n_samples), start=1):
        sample_id = f"public_{output_name}_{idx:04d}"

        audio_path = raw_dir / f"{sample_id}.wav"
        text_path = raw_dir / f"{sample_id}.txt"

        try:
            sample_rate = save_audio_from_hf_sample(sample, audio_path)
        except Exception as e:
            print(f"[SKIP] {sample_id}: cannot save audio: {e}")
            continue

        transcript = get_text(sample)
        text_path.write_text(transcript, encoding="utf-8")

        audio_checksum = sha256_file(audio_path)
        text_checksum = sha256_file(text_path)

        row = {
            "sample_id": sample_id,
            "dataset_id": dataset_id,
            "source_name": source_name,
            "source_type": "public",
            "domain": domain,
            "split_role": "smoke_test",
            "raw_audio_path": str(audio_path.relative_to(PROJECT_ROOT)),
            "raw_transcript_path": str(text_path.relative_to(PROJECT_ROOT)),
            "transcript_text": transcript,
            "language": "vi-VN",
            "sample_rate_hz": sample_rate,
            "audio_checksum_sha256": audio_checksum,
            "text_checksum_sha256": text_checksum,
            "license_status": license_status,
            "allowed_use": allowed_use,
            "target_zone": ["bronze", "silver"],
            "contains_phi": "unknown",
            "consent_status": "not_applicable",
            "governance_status": governance_status,
            "wer_eval_allowed": True,
            "train_allowed": license_status in ["clear", "internal"] and "training" in allowed_use,
            "commercial_pilot_status": "needs_review",
            "created_at": now_iso(),
            "created_by": CREATED_BY,
            "version": VERSION,
            "notes": "Day 1 smoke ingest. Not Gold. Not training-ready unless governance/license is clear."
        }

        rows.append(row)
        checksum_lines.append(f"{audio_checksum}  {audio_path.name}")
        checksum_lines.append(f"{text_checksum}  {text_path.name}")

    write_jsonl(metadata_dir / "manifest_raw.jsonl", rows)
    (checksum_dir / "checksums.sha256").write_text("\n".join(checksum_lines), encoding="utf-8")

    license_note = f"""# License Snapshot — {source_name}

Source: {dataset_name}
Config: {dataset_config}
Split: {split}
Ingested at: {now_iso()}

License status in this MVP registry: {license_status}
Governance status: {governance_status}

Notes:
- This is a local Bronze/Silver ingest.
- This source is not Gold.
- Do not use for training unless license/governance is clear.
"""
    (license_dir / "LICENSE_SNAPSHOT.md").write_text(license_note, encoding="utf-8")

    print(f"[DONE] {source_name}: {len(rows)} samples saved to {output_root}")


def main():
    hf_token = os.environ.get("HF_TOKEN")

    # 1. VietMed smoke subset
    ingest_hf_streaming_dataset(
        dataset_name="leduckhai/VietMed",
        dataset_config=None,
        split="train",
        source_name="VietMed",
        dataset_id="asr_vietmed_001",
        domain="medical_speech",
        output_name="vietmed",
        n_samples=50,
        license_status="needs_review",
        governance_status="needs_legal_review",
        allowed_use=["evaluation", "reference_only"],
        token=hf_token,
    )

    # 2. FOSD via HF mirror, use only if you accept mirror risk
    ingest_hf_streaming_dataset(
        dataset_name="doof-ferb/fpt_fosd",
        dataset_config=None,
        split="train",
        source_name="FOSD",
        dataset_id="asr_fosd_001",
        domain="general_speech",
        output_name="fosd",
        n_samples=50,
        license_status="needs_review",
        governance_status="pending_review",
        allowed_use=["evaluation", "reference_only"],
        token=hf_token,
    )

    # 3. Common Voice note:
    # Because official Common Voice distribution moved to Mozilla Data Collective,
    # prefer manual official download, then write a separate local parser.
    print("[NOTE] Common Voice vi should preferably be downloaded from Mozilla Data Collective.")
    print("[NOTE] After download, parse validated.tsv/train.tsv and clips/ into bronze/public/common_voice_vi.")


if __name__ == "__main__":
    main()