import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.data_ingestion.normalize_public_audio import (
    sha256_file,
    read_jsonl,
    write_jsonl,
    ffmpeg_normalize,
    ffprobe_duration,
)

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

def test_read_write_jsonl(temp_dir):
    file_path = temp_dir / "test.jsonl"
    data = [{"id": 1, "text": "hello"}, {"id": 2, "text": "world"}]
    
    write_jsonl(file_path, data)
    assert file_path.exists()
    
    read_data = read_jsonl(file_path)
    assert len(read_data) == 2
    assert read_data[0]["text"] == "hello"

def test_read_jsonl_not_exists(temp_dir):
    file_path = temp_dir / "not_exists.jsonl"
    assert read_jsonl(file_path) == []

def test_sha256_file(temp_dir):
    file_path = temp_dir / "test.txt"
    file_path.write_text("dummy content")
    
    # sha256 of "dummy content" is b42a22285a854a8809033ea641bf1cd144fb44b58e727b140e4eab5929d29094
    expected_hash = "b42a22285a854a8809033ea641bf1cd144fb44b58e727b140e4eab5929d29094"
    assert sha256_file(file_path) == expected_hash

@patch("scripts.data_ingestion.normalize_public_audio.subprocess.run")
def test_ffmpeg_normalize(mock_run, temp_dir):
    raw_path = temp_dir / "raw.wav"
    clean_path = temp_dir / "clean.wav"
    
    ffmpeg_normalize(raw_path, clean_path)
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "ffmpeg" in args[0]
    assert "-ar" in args[0]
    assert "16000" in args[0]
    assert "-ac" in args[0]
    assert "1" in args[0]

@patch("scripts.data_ingestion.normalize_public_audio.subprocess.run")
def test_ffprobe_duration(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = "12.3456\n"
    mock_run.return_value = mock_result
    
    duration = ffprobe_duration(Path("dummy.wav"))
    assert duration == 12.346

@patch("scripts.data_ingestion.normalize_public_audio.subprocess.run")
def test_ffprobe_duration_error(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = "invalid\n"
    mock_run.return_value = mock_result
    
    duration = ffprobe_duration(Path("dummy.wav"))
    assert duration is None
