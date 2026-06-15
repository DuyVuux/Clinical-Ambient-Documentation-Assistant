#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "asr_vimedcss"))

from importlib import import_module

mod = import_module("02_create_vimedcss_run_manifests_and_archives")

resolve_audio = mod.resolve_audio
build_audio_roots = mod.build_audio_roots
materialize = mod.materialize
audio_ref = mod.audio_ref
normalize_run_row = mod.normalize_run_row
make_feat = mod.make_feat


class TestResolveAudio:
    def test_none_ref_returns_none(self):
        assert resolve_audio(None, []) is None

    def test_empty_ref_returns_none(self):
        assert resolve_audio("", []) is None

    def test_absolute_path_exists(self, tmp_path):
        wav = tmp_path / "test.wav"
        wav.touch()
        result = resolve_audio(str(wav), [])
        assert result == wav

    def test_relative_path_direct_match(self, tmp_path):
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        wav = audio_dir / "sample.wav"
        wav.touch()
        result = resolve_audio("audio/sample.wav", [tmp_path])
        assert result == wav

    def test_basename_only_match(self, tmp_path):
        sub = tmp_path / "data" / "vimedcss_audio"
        sub.mkdir(parents=True)
        wav = sub / "Med_CS-0-1.wav"
        wav.touch()
        result = resolve_audio("Med_CS-0-1.wav", [sub])
        assert result == wav

    def test_basename_fallback_from_nested_path(self, tmp_path):
        sub = tmp_path / "nested"
        sub.mkdir()
        wav = sub / "Med_CS-4374-8.wav"
        wav.touch()
        result = resolve_audio("some/other/path/Med_CS-4374-8.wav", [sub])
        assert result == wav

    def test_rglob_fallback(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        wav = deep / "deep_audio.wav"
        wav.touch()
        result = resolve_audio("deep_audio.wav", [tmp_path])
        assert result == wav

    def test_no_match_returns_none(self, tmp_path):
        result = resolve_audio("nonexistent.wav", [tmp_path])
        assert result is None


class TestBuildAudioRoots:
    def test_includes_data_vimedcss_audio(self, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        data_audio = project / "data" / "vimedcss_audio"
        data_audio.mkdir(parents=True)
        vroot = project / "experiments" / "asr" / "vimedcss"
        vroot.mkdir(parents=True)
        (project / "data").mkdir(exist_ok=True)

        roots = build_audio_roots(vroot)
        root_strs = [str(r) for r in roots]
        assert str(data_audio) in root_strs

    def test_extra_roots_prepended(self, tmp_path):
        extra = tmp_path / "extra_audio"
        extra.mkdir()
        vroot = tmp_path / "vroot"
        vroot.mkdir()
        roots = build_audio_roots(vroot, [extra])
        assert roots[0] == extra

    def test_no_duplicates(self, tmp_path):
        vroot = tmp_path / "vroot"
        vroot.mkdir()
        roots = build_audio_roots(vroot)
        assert len(roots) == len(set(roots))


class TestAudioRef:
    def test_string_audio(self):
        ref, field = audio_ref({"audio": "test.wav"})
        assert ref == "test.wav"
        assert field == "audio"

    def test_dict_audio_path(self):
        ref, field = audio_ref({"audio": {"path": "file.wav"}})
        assert ref == "file.wav"
        assert field == "audio.path"

    def test_fallback_audio_path_key(self):
        ref, field = audio_ref({"audio_path": "fallback.wav"})
        assert ref == "fallback.wav"
        assert field == "audio_path"

    def test_no_audio_returns_none(self):
        ref, field = audio_ref({})
        assert ref is None
        assert field is None


class TestMaterialize:
    def test_manifests_only_mode(self, tmp_path):
        manifest_path = tmp_path / "test.jsonl"
        rows = [{"sample_id": "s1", "duration_seconds": 10.0}]

        result = materialize(
            "test_subset", rows, manifest_path,
            tmp_path, tmp_path, tmp_path / "archives",
            None, True, False
        )

        assert result["mode"] == "manifests_only"
        assert result["local_archive_path"] is None
        assert result["drive_archive_path"] is None
        assert result["rows"] == 1
        assert manifest_path.exists()

        written = [json.loads(line) for line in manifest_path.read_text().strip().split("\n")]
        assert len(written) == 1
        assert written[0]["sample_id"] == "s1"

    def test_materialize_with_audio(self, tmp_path):
        audio_dir = tmp_path / "audio_src"
        audio_dir.mkdir()
        wav = audio_dir / "test.wav"
        wav.write_bytes(b"RIFF" + b"\x00" * 100)

        manifest_path = tmp_path / "manifest.jsonl"
        rows = [{"sample_id": "s1", "audio": "test.wav", "duration_seconds": 5.0}]

        result = materialize(
            "test_subset", rows, manifest_path,
            tmp_path, tmp_path, tmp_path / "archives",
            None, False, False, [audio_dir]
        )

        assert result["mode"] == "materialized_archive"
        assert result["copied_audio"] == 1
        assert result["missing_audio"] == 0
        assert result["local_archive_path"] is not None


class TestMakeFeat:
    def test_basic_valid_sample(self):
        row = {
            "segment_id": "test_001",
            "segment_text": "Bệnh nhân có triệu chứng COVID-19",
            "duration_seconds": 5.0,
            "audio": "test.wav",
            "topic": "COVID",
            "cs_terms_list": ["COVID-19"],
            "cs_terms_count": 1,
        }
        feat = make_feat(row, "train", 0, set())
        assert feat["is_basic_valid"] is True
        assert feat["segment_id"] == "test_001"
        assert feat["is_suspect"] is False

    def test_suspect_sample_excluded(self):
        row = {
            "segment_id": "suspect_001",
            "segment_text": "test text here",
            "duration_seconds": 5.0,
            "audio": "test.wav",
        }
        feat = make_feat(row, "train", 0, {"suspect_001"})
        assert feat["is_suspect"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
