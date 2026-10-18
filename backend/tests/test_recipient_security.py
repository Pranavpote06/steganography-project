import io
import pytest
import numpy as np
import scipy.io.wavfile as wavfile
from fastapi.testclient import TestClient
from app.main import app
from app.services.audio_stego import embed_audio_data, extract_audio_data
from app.services.otp_service import otp_service
from app.services.audit_service import audit_service
from app.core.security import InvalidPasswordError

client = TestClient(app)

@pytest.fixture
def sample_wav(tmp_path):
    sample_rate = 22050
    duration = 1.0
    num_samples = int(sample_rate * duration)
    data = (np.sin(np.linspace(0, duration, num_samples)) * 10000).astype(np.int16)
    carrier_path = str(tmp_path / "carrier.wav")
    wavfile.write(carrier_path, sample_rate, data)
    return carrier_path

def test_embed_and_extract_with_recipient_phone(sample_wav, tmp_path):
    output_wav = str(tmp_path / "stego_phone.wav")
    secret_text = "SECRET_INTEL_FOR_AGENT_BOND"
    recipient_phone = "+1 (555) 019-2834"
    sender_id = "M-Branch"

    # 1. Embed with recipient phone
    res = embed_audio_data(
        input_path=sample_wav,
        output_path=output_wav,
        raw_payload=secret_text.encode("utf-8"),
        recipient_phone=recipient_phone,
        sender_id=sender_id
    )
    assert res["status"] == "success"
    assert res["require_recipient_verify"] is True

    # 2. Extract without phone should fail
    with pytest.raises(InvalidPasswordError):
        extract_audio_data(output_wav, recipient_phone=None)

    # 3. Extract with wrong phone should fail
    with pytest.raises(InvalidPasswordError, match="not authorized"):
        extract_audio_data(output_wav, recipient_phone="+1 (555) 999-9999")

    # 4. Extract with correct phone recovers payload
    recovered = extract_audio_data(output_wav, recipient_phone="+1 555-019-2834")
    assert recovered.content.decode("utf-8") == secret_text
    assert recovered.sender_id == sender_id

def test_otp_generation_and_verification():
    phone = "+1 555-0144"
    res = otp_service.generate_otp(phone)
    session_token = res["session_token"]
    otp_code = otp_service._sessions[session_token]["otp"]

    # Wrong OTP
    assert otp_service.verify_otp(session_token, "000000") is False

    # Correct OTP
    assert otp_service.verify_otp(session_token, otp_code) is True

def test_audit_service_face_capture():
    # 1x1 dummy JPEG base64
    dummy_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    entry = audit_service.record_access_attempt(
        carrier_filename="test_stego.wav",
        media_type="audio",
        recipient_phone="+1 555-0199",
        sender_id="Commander",
        status="SUCCESS_UNLOCKED",
        face_base64=dummy_b64
    )
    assert entry["id"].startswith("audit_")
    assert entry["has_face_capture"] is True

    logs = audit_service.get_audit_logs()
    assert len(logs) > 0
    assert logs[0]["id"] == entry["id"]

def test_security_api_endpoints(sample_wav):
    # 1. Embed a test file with recipient verification
    with open(sample_wav, "rb") as f:
        audio_bytes = f.read()

    embed_res = client.post(
        "/api/audio/embed",
        data={
            "payload_type": "text",
            "secret_text": "TOP_SECRET_COORDINATES",
            "recipient_phone": "+1 555 019 7777",
            "sender_id": "HQ-Sentinel"
        },
        files={"audio_file": ("test.wav", audio_bytes, "audio/wav")}
    )
    assert embed_res.status_code == 200
    stego_id = embed_res.json()["download_id"]

    # 2. Download stego audio
    dl_res = client.get(f"/api/audio/download/{stego_id}")
    stego_wav_bytes = dl_res.content

    # 3. Test Inspect API
    insp_res = client.post(
        "/api/security/inspect",
        files={"carrier_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert insp_res.status_code == 200
    insp_data = insp_res.json()
    assert insp_data["has_stego"] is True
    assert insp_data["has_recipient_verify"] is True
    assert "masked_phone" in insp_data

    # 4. Request OTP with unauthorized phone
    bad_otp_res = client.post(
        "/api/security/request-otp",
        data={"recipient_phone": "+1 555 999 0000"},
        files={"carrier_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert bad_otp_res.status_code == 403

    # 5. Request OTP with authorized phone
    good_otp_res = client.post(
        "/api/security/request-otp",
        data={"recipient_phone": "+1 555 019 7777"},
        files={"carrier_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert good_otp_res.status_code == 200
    otp_data = good_otp_res.json()
    session_token = otp_data["session_token"]
    otp_code = otp_service._sessions[session_token]["otp"]

    # 6a. Attempt extraction without a human face (blank black image) - must be REJECTED
    import cv2
    import base64
    test_img = np.zeros((120, 120, 3), dtype=np.uint8)
    _, img_buf = cv2.imencode(".jpg", test_img)
    test_img_b64 = "data:image/jpeg;base64," + base64.b64encode(img_buf).decode("utf-8")

    extract_blank_res = client.post(
        "/api/security/verify-and-extract",
        data={
            "session_token": session_token,
            "phone": "+1 555 019 7777",
            "otp": otp_code,
            "face_image": test_img_b64
        },
        files={"carrier_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
    )
    assert extract_blank_res.status_code == 400
    assert "No person detected" in extract_blank_res.json()["detail"]

    # 6b. Verify and Extract with valid face detection
    from unittest.mock import patch
    with patch("app.api.routes_security.face_detector.detect_face_and_mask") as mock_detect:
        mock_detect.return_value = {
            "has_face": True,
            "is_unmasked": True,
            "is_valid": True,
            "status": "FACE_VALID",
            "message": "Full unmasked face verified — both eyes, nose and lips detected.",
            "bbox": [50, 50, 200, 200],
            "confidence": 0.95
        }
        extract_res = client.post(
            "/api/security/verify-and-extract",
            data={
                "session_token": session_token,
                "phone": "+1 555 019 7777",
                "otp": otp_code,
                "face_image": test_img_b64
            },
            files={"carrier_file": ("stego.wav", stego_wav_bytes, "audio/wav")}
        )
        assert extract_res.status_code == 200
        ext_data = extract_res.json()
        assert ext_data["text"] == "TOP_SECRET_COORDINATES"
        assert ext_data["face_captured"] is True
        audit_id = ext_data["audit_id"]

    # 7. Check Audit Logs API
    audit_res = client.get("/api/security/audit-logs")
    assert audit_res.status_code == 200
    logs = audit_res.json()["logs"]
    assert any(log["id"] == audit_id for log in logs)

    # 8. Check Face image serving API
    face_res = client.get(f"/api/security/face/{audit_id}")
    assert face_res.status_code == 200
    assert face_res.headers["content-type"] == "image/jpeg"
