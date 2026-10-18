import os
import pytest
import numpy as np
import scipy.io.wavfile as wavfile
from app.services.audio_stego import (
    embed_audio_data,
    extract_audio_data,
    get_audio_info,
    InsufficientCapacityError,
    AudioStegoError
)
from app.core.security import InvalidPasswordError

@pytest.fixture
def sample_wav(tmp_path):
    """Generates a synthetic 2-second 44.1kHz stereo 16-bit PCM WAV file."""
    sample_rate = 44100
    duration = 2.0
    num_samples = int(sample_rate * duration)
    # Generate 440Hz sine wave
    t = np.linspace(0, duration, num_samples, False)
    tone = np.sin(2 * np.pi * 440 * t)
    audio_data = (tone * 16384).astype(np.int16)
    stereo_data = np.column_stack((audio_data, audio_data))
    
    file_path = tmp_path / "carrier.wav"
    wavfile.write(str(file_path), sample_rate, stereo_data)
    return str(file_path)

def test_audio_embed_extract_text(sample_wav, tmp_path):
    output_wav = str(tmp_path / "stego_text.wav")
    secret_text = "CYBER_OP_PHANTOM_2026: Mission authorized at sector 7."
    
    res = embed_audio_data(
        input_path=sample_wav,
        output_path=output_wav,
        raw_payload=secret_text.encode("utf-8"),
        is_file=False
    )
    assert res["status"] == "success"
    assert res["payload_bytes"] == len(secret_text.encode("utf-8"))
    
    extracted = extract_audio_data(output_wav)
    assert not extracted.is_file
    assert extracted.content.decode("utf-8") == secret_text

def test_audio_embed_extract_file_encrypted(sample_wav, tmp_path):
    output_wav = str(tmp_path / "stego_file.wav")
    file_bytes = b"BINARY_DATA_%PDF-1.4_TEST_PAYLOAD_BYTE_STREAM_EXACT_RECOVERY"
    password = "AudioCyberKey2026!"
    
    embed_audio_data(
        input_path=sample_wav,
        output_path=output_wav,
        raw_payload=file_bytes,
        is_file=True,
        filename="intel_document.pdf",
        mime_type="application/pdf",
        password=password
    )
    
    # Extraction without password fails
    with pytest.raises(InvalidPasswordError):
        extract_audio_data(output_wav, password=None)
        
    # Extraction with wrong password fails
    with pytest.raises(InvalidPasswordError):
        extract_audio_data(output_wav, password="WrongPassword")
        
    # Extraction with correct password recovers exact file
    recovered = extract_audio_data(output_wav, password=password)
    assert recovered.is_file
    assert recovered.filename == "intel_document.pdf"
    assert recovered.mime_type == "application/pdf"
    assert recovered.content == file_bytes

def test_audio_insufficient_capacity(tmp_path):
    """A tiny audio file (100 samples) cannot hold a 1KB payload."""
    tiny_wav = str(tmp_path / "tiny.wav")
    data = np.zeros(100, dtype=np.int16)
    wavfile.write(tiny_wav, 8000, data)
    
    large_payload = b"X" * 1024
    output_wav = str(tmp_path / "stego_fail.wav")
    
    with pytest.raises(InsufficientCapacityError):
        embed_audio_data(tiny_wav, output_wav, large_payload)

def test_audio_no_stego_detected(sample_wav):
    """An untouched original carrier audio should report no stego signature."""
    with pytest.raises(AudioStegoError, match="No hidden steganography payload detected"):
        extract_audio_data(sample_wav)

def test_audio_get_info(sample_wav):
    info = get_audio_info(sample_wav)
    assert info["sample_rate"] == 44100
    assert info["channels"] == 2
    assert info["capacity_bytes"] > 0
