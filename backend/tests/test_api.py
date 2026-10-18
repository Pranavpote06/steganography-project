import io
import pytest
import numpy as np
import scipy.io.wavfile as wavfile
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["ffmpeg_available"] is True

def test_api_stats():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_processed" in data
    assert "recent_operations" in data

def test_audio_embed_extract_flow():
    # 1. Create in-memory WAV
    sample_rate = 22050
    audio_data = (np.sin(np.linspace(0, 1.0, sample_rate)) * 10000).astype(np.int16)
    wav_io = io.BytesIO()
    wavfile.write(wav_io, sample_rate, audio_data)
    wav_io.seek(0)
    
    # 2. Check capacity endpoint
    cap_res = client.post(
        "/api/audio/capacity",
        files={"audio_file": ("test.wav", wav_io.getvalue(), "audio/wav")}
    )
    assert cap_res.status_code == 200
    assert cap_res.json()["capacity_bytes"] > 0
    
    # 3. Embed text
    secret_text = "Classified API Message #404"
    embed_res = client.post(
        "/api/audio/embed",
        data={
            "payload_type": "text",
            "secret_text": secret_text,
            "password": "ApiPassword123"
        },
        files={"audio_file": ("test.wav", wav_io.getvalue(), "audio/wav")}
    )
    assert embed_res.status_code == 200
    embed_data = embed_res.json()
    assert embed_data["status"] == "success"
    download_id = embed_data["download_id"]
    
    # 4. Download generated stego WAV
    dl_res = client.get(f"/api/audio/download/{download_id}")
    assert dl_res.status_code == 200
    stego_wav_bytes = dl_res.content
    
    # 5. Extract with wrong password
    ext_fail_res = client.post(
        "/api/audio/extract",
        data={"password": "WrongPassword"},
        files={"audio_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert ext_fail_res.status_code == 401
    
    # 6. Extract with correct password
    ext_success_res = client.post(
        "/api/audio/extract",
        data={"password": "ApiPassword123"},
        files={"audio_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert ext_success_res.status_code == 200
    ext_data = ext_success_res.json()
    assert ext_data["is_file"] is False
    assert ext_data["text"] == secret_text
