import os
import uuid
import base64
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from ..core import config
from ..core.config import TEMP_DIR, MAX_UPLOAD_SIZE, ALLOWED_VIDEO_EXTENSIONS
from ..services.audio_stego import inspect_audio_carrier, extract_audio_data
from ..services.video_stego import inspect_video_carrier, extract_video_data
from ..services.otp_service import otp_service
from ..services.audit_service import audit_service
from ..core.security import InvalidPasswordError
from ..core.payload import PayloadError, normalize_phone, mask_phone
from ..services.stats_service import stats_tracker
from ..services.face_detector_service import face_detector

router = APIRouter()

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@router.post("/inspect")
async def inspect_carrier(carrier_file: UploadFile = File(...)):
    """
    Inspects an uploaded carrier file to check whether it contains a stego payload,
    and whether it requires recipient phone verification & face scan.
    """
    ext = Path(carrier_file.filename).suffix.lower()
    is_audio = ext in {".wav", ".mp3"}
    is_video = ext in ALLOWED_VIDEO_EXTENSIONS

    if not is_audio and not is_video:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported media format '{ext}'. Supported: .wav, .mp3, .mp4, .avi, .mov, .mkv"
        )

    temp_path = TEMP_DIR / f"insp_{uuid.uuid4().hex}{ext}"
    try:
        content = await carrier_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File exceeds maximum size.")
        with open(temp_path, "wb") as f:
            f.write(content)

        if is_audio:
            info = await asyncio.to_thread(inspect_audio_carrier, str(temp_path))
        else:
            info = await asyncio.to_thread(inspect_video_carrier, str(temp_path))

        info["filename"] = carrier_file.filename
        info["media_type"] = "audio" if is_audio else "video"
        info.pop("stored_phone", None)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect carrier: {str(e)}")
    finally:
        cleanup_file(str(temp_path))

@router.post("/request-otp")
async def request_otp(
    carrier_file: UploadFile = File(...),
    recipient_phone: str = Form(...)
):
    """
    Validates recipient phone against the embedded carrier metadata,
    and dispatches a 6-digit OTP.
    """
    ext = Path(carrier_file.filename).suffix.lower()
    is_audio = ext in {".wav", ".mp3"}
    is_video = ext in ALLOWED_VIDEO_EXTENSIONS

    if not is_audio and not is_video:
        raise HTTPException(status_code=400, detail="Unsupported media format.")

    temp_path = TEMP_DIR / f"otp_req_{uuid.uuid4().hex}{ext}"
    try:
        content = await carrier_file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        info = inspect_audio_carrier(str(temp_path)) if is_audio else inspect_video_carrier(str(temp_path))

        if not info.get("has_stego"):
            raise HTTPException(status_code=400, detail="No steganography payload detected in this media.")

        if not info.get("has_recipient_verify"):
            raise HTTPException(status_code=400, detail="This carrier does not require phone verification. Use standard extraction.")

        # Check phone number match
        clean_input = normalize_phone(recipient_phone)
        stored_masked = info.get("masked_phone", "")
        stored_raw = info.get("stored_phone", "")

        if stored_raw:
            norm_stored = normalize_phone(stored_raw)
            if clean_input != norm_stored and clean_input[-10:] != norm_stored[-10:]:
                audit_service.record_access_attempt(
                    carrier_filename=carrier_file.filename,
                    media_type="audio" if is_audio else "video",
                    recipient_phone=recipient_phone,
                    status="FAILED_UNAUTHORIZED_PHONE",
                    payload_name="Blocked Access"
                )
                raise HTTPException(status_code=403, detail="Access Denied: This phone number is not authorized to unlock this confidential file.")

        # Generate and dispatch OTP
        otp_res = otp_service.generate_otp(recipient_phone, carrier_file.filename)

        return {
            "status": "otp_dispatched",
            "session_token": otp_res["session_token"],
            "phone": recipient_phone,
            "masked_phone": stored_masked,
            "expires_in": otp_res["expires_in"],
            "sms_sent": otp_res.get("sms_sent", False),
            "sms_gateway": otp_res.get("sms_gateway", "none"),
            "sms_status_message": otp_res.get("sms_status_message", "SMS dispatched to phone.")
        }
    finally:
        cleanup_file(str(temp_path))

@router.post("/verify-and-extract")
async def verify_and_extract(
    carrier_file: UploadFile = File(...),
    face_image: str = Form(...), # Base64 data URI from webcam capture
    password: Optional[str] = Form(None),
    session_token: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    otp: Optional[str] = Form(None)
):
    """
    Verifies the recipient's live webcam biometric face scan (blocks if mask/hidden face),
    logs the event in the audit vault, and recovers the hidden payload using the password.
    """
    # 1. Verify OTP only if session_token and otp were explicitly provided (backward-compat)
    if session_token and otp:
        if not otp_service.verify_otp(session_token, otp):
            audit_service.record_access_attempt(
                carrier_filename=carrier_file.filename,
                media_type="unknown",
                recipient_phone=phone or "Password User",
                status="FAILED_INVALID_OTP",
                face_base64=face_image,
                payload_name="Invalid OTP Attempt"
            )
            raise HTTPException(status_code=401, detail="Invalid or expired OTP code.")

    # 1.5 Strict Face Verification & Anti-Mask Detection
    if not face_image or not face_image.strip():
        raise HTTPException(
            status_code=400,
            detail="Face Verification Blocked: No camera image provided. Live biometric scan is required."
        )

    decoded_face = face_detector.decode_base64_image(face_image)
    if decoded_face is None or decoded_face.size == 0:
        raise HTTPException(
            status_code=400,
            detail="Face Verification Blocked: Invalid camera image stream."
        )

    detection_res = face_detector.detect_face_and_mask(decoded_face)
    if not detection_res.get("has_face"):
        audit_service.record_access_attempt(
            carrier_filename=carrier_file.filename,
            media_type="unknown",
            recipient_phone=phone or "User",
            status="FAILED_NO_FACE",
            face_base64=face_image,
            payload_name="Blocked - No Person in Frame"
        )
        raise HTTPException(
            status_code=400,
            detail="Face Verification Blocked: No person detected in the camera frame. The person must be clearly visible in front of the camera."
        )

    if not detection_res.get("is_valid") or not detection_res.get("is_unmasked"):
        audit_service.record_access_attempt(
            carrier_filename=carrier_file.filename,
            media_type="unknown",
            recipient_phone=phone or "User",
            status="FAILED_FACE_INVALID",
            face_base64=face_image,
            payload_name="Blocked - Face Incomplete or Masked"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Face Verification Blocked: {detection_res.get('message', 'Full face with eyes, nose and lips without mask required.')}"
        )

    # 2. Extract media
    ext = Path(carrier_file.filename).suffix.lower()
    is_audio = ext in {".wav", ".mp3"}
    temp_path = TEMP_DIR / f"ver_ext_{uuid.uuid4().hex}{ext}"

    try:
        content = await carrier_file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        clean_phone = normalize_phone(phone) if phone else None
        if is_audio:
            stego_data = await asyncio.to_thread(extract_audio_data, str(temp_path), password=password, recipient_phone=clean_phone)
        else:
            stego_data = await asyncio.to_thread(extract_video_data, str(temp_path), password=password, recipient_phone=clean_phone)

        payload_name = stego_data.filename if stego_data.is_file else "Secret Text Payload"
        payload_type = "file" if stego_data.is_file else "text"

        # 3. Record Audit and Save Face Capture for the Sender
        audit_entry = audit_service.record_access_attempt(
            carrier_filename=carrier_file.filename,
            media_type="audio" if is_audio else "video",
            recipient_phone=phone,
            sender_id=stego_data.sender_id,
            status="SUCCESS_UNLOCKED",
            face_base64=face_image,
            payload_name=payload_name,
            payload_type=payload_type
        )

        stats_tracker.record_operation(
            op_type="extract",
            media_type="audio" if is_audio else "video",
            payload_type=payload_type,
            payload_name=payload_name,
            media_name=carrier_file.filename,
            file_size_bytes=len(stego_data.content),
            encrypted=True,
            success=True
        )

        if stego_data.is_file:
            b64_content = base64.b64encode(stego_data.content).decode("utf-8")
            return {
                "status": "success",
                "is_file": True,
                "filename": stego_data.filename or "recovered_file.bin",
                "mime_type": stego_data.mime_type or "application/octet-stream",
                "file_size": len(stego_data.content),
                "data_base64": b64_content,
                "audit_id": audit_entry["id"],
                "face_captured": True,
                "sender_id": stego_data.sender_id
            }
        else:
            decoded_text = stego_data.content.decode("utf-8", errors="replace")
            return {
                "status": "success",
                "is_file": False,
                "text": decoded_text,
                "length": len(decoded_text),
                "audit_id": audit_entry["id"],
                "face_captured": True,
                "sender_id": stego_data.sender_id
            }

    except InvalidPasswordError as e:
        audit_service.record_access_attempt(
            carrier_filename=carrier_file.filename,
            media_type="audio" if is_audio else "video",
            recipient_phone=phone,
            status="FAILED_DECRYPTION",
            face_base64=face_image,
            payload_name="Decryption Failure"
        )
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
    finally:
        cleanup_file(str(temp_path))

@router.get("/audit-logs")
def get_audit_logs(sender_id: Optional[str] = None):
    """Returns access logs and captured face scans for the sender."""
    return {
        "count": len(audit_service.get_audit_logs(sender_id)),
        "logs": audit_service.get_audit_logs(sender_id)
    }

@router.get("/face/{audit_id}")
def get_captured_face(audit_id: str):
    """Serves the captured face image to the sender."""
    img_path = audit_service.get_face_image_path(audit_id)
    if not img_path or not img_path.exists():
        raise HTTPException(status_code=404, detail="Captured face image not found.")
    return FileResponse(path=str(img_path), media_type="image/jpeg")

@router.post("/detect-face")
async def detect_face_realtime(face_frame: str = Form(...)):
    """Real-time live video frame face tracking & mask detection endpoint."""
    img = face_detector.decode_base64_image(face_frame)
    if img is None:
        return {"has_face": False, "is_unmasked": False, "is_valid": False, "status": "NO_FRAME", "message": "No frame received."}
    return face_detector.detect_face_and_mask(img)

@router.post("/audit-logs/clear")
def clear_audit_logs():
    """Clears all audit logs and captured images."""
    audit_service.clear_logs()
    return {"message": "Audit logs and captured biometric photos cleared."}

@router.get("/sms-status")
def get_sms_status():
    """Returns the operational status of SMS gateways."""
    has_twilio = bool(config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_FROM_NUMBER)
    has_fast2sms = bool(config.FAST2SMS_API_KEY)
    has_twofactor = bool(config.TWOFACTOR_API_KEY)
    has_webhook = bool(config.SMS_WEBHOOK_URL)

    active_provider = "none"
    if has_twilio:
        active_provider = "twilio"
    elif has_fast2sms:
        active_provider = "fast2sms"
    elif has_twofactor:
        active_provider = "2factor"
    elif has_webhook:
        active_provider = "webhook"

    return {
        "active_provider": active_provider,
        "twilio_configured": has_twilio,
        "fast2sms_configured": has_fast2sms,
        "twofactor_configured": has_twofactor,
        "webhook_configured": has_webhook,
        "twilio_number": config.TWILIO_FROM_NUMBER if has_twilio else None
    }

@router.post("/sms-config")
async def update_sms_config(
    twilio_sid: Optional[str] = Form(None),
    twilio_token: Optional[str] = Form(None),
    twilio_from: Optional[str] = Form(None),
    fast2sms_key: Optional[str] = Form(None),
    twofactor_key: Optional[str] = Form(None)
):
    """Updates SMS gateway configuration and persists to backend/.env."""
    env_lines = []
    env_file = config.ENV_PATH

    existing_vars = {}
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str and not line_str.startswith("#") and "=" in line_str:
                    k, v = line_str.split("=", 1)
                    existing_vars[k.strip()] = v.strip()

    if twilio_sid is not None:
        config.TWILIO_ACCOUNT_SID = twilio_sid.strip()
        existing_vars["TWILIO_ACCOUNT_SID"] = twilio_sid.strip()
    if twilio_token is not None:
        config.TWILIO_AUTH_TOKEN = twilio_token.strip()
        existing_vars["TWILIO_AUTH_TOKEN"] = twilio_token.strip()
    if twilio_from is not None:
        config.TWILIO_FROM_NUMBER = twilio_from.strip()
        existing_vars["TWILIO_FROM_NUMBER"] = twilio_from.strip()
    if fast2sms_key is not None:
        config.FAST2SMS_API_KEY = fast2sms_key.strip()
        existing_vars["FAST2SMS_API_KEY"] = fast2sms_key.strip()
    if twofactor_key is not None:
        config.TWOFACTOR_API_KEY = twofactor_key.strip()
        existing_vars["TWOFACTOR_API_KEY"] = twofactor_key.strip()

    # Write back to backend/.env
    with open(env_file, "w", encoding="utf-8") as f:
        for k, v in existing_vars.items():
            f.write(f"{k}={v}\n")

    active = "none"
    if config.TWILIO_ACCOUNT_SID:
        active = "twilio"
    elif config.FAST2SMS_API_KEY:
        active = "fast2sms"
    elif config.TWOFACTOR_API_KEY:
        active = "2factor"

    return {
        "status": "updated",
        "active_provider": active
    }
