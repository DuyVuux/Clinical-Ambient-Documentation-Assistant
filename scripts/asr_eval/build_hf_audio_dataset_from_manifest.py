#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path

from datasets import Audio, Dataset


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--sampling_rate", type=int, default=16000)

    args = parser.parse_args()

    manifest = Path(args.manifest)
    output_dir = Path(args.output_dir)

    dataset = Dataset.from_json(str(manifest))
    dataset = dataset.cast_column("audio", Audio(sampling_rate=args.sampling_rate))

    output_dir.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(output_dir))

    print(dataset)
    print(f"[DONE] saved to: {output_dir}")


if __name__ == "__main__":
    main()