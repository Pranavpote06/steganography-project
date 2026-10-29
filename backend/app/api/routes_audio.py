import os
import uuid
import base64
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from ..core.config import TEMP_DIR, MAX_UPLOAD_SIZE
from ..services.audio_stego import (
    embed_audio_data,
    extract_audio_data,
    get_audio_info,
    AudioStegoError,
    InsufficientCapacityError
)
from ..core.security import InvalidPasswordError
from ..core.payload import PayloadError
from ..services.stats_service import stats_tracker

router = APIRouter()

def cleanup_file(path: str):
    """Safely removes temporary files."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@router.post("/capacity")
async def audio_capacity(audio_file: UploadFile = File(...)):
    """Inspects an audio file (WAV or MP3) and calculates its steganographic capacity."""
    fname_lower = audio_file.filename.lower()
    if not (fname_lower.endswith(".wav") or fname_lower.endswith(".mp3")):
        raise HTTPException(status_code=400, detail="Only WAV and MP3 formats are supported for audio steganography.")

    ext = ".mp3" if fname_lower.endswith(".mp3") else ".wav"
    temp_path = TEMP_DIR / f"cap_{uuid.uuid4().hex}{ext}"
    try:
        content = await audio_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum upload size of {MAX_UPLOAD_SIZE // (1024*1024)}MB.")
        with open(temp_path, "wb") as f:
            f.write(content)

        info = await asyncio.to_thread(get_audio_info, str(temp_path))
        info["filename"] = audio_file.filename
        info["file_size_bytes"] = len(content)
        return info
    except AudioStegoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze audio: {str(e)}")
    finally:
        cleanup_file(str(temp_path))

@router.post("/embed")
async def audio_embed(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    payload_type: str = Form(...), # "text" or "file"
    secret_text: Optional[str] = Form(None),
    secret_file: Optional[UploadFile] = File(None),
    password: Optional[str] = Form(None),
    require_face_scan: bool = Form(False),
    recipient_phone: Optional[str] = Form(None),
    sender_id: Optional[str] = Form(None)
):
    """Embeds confidential text or file into a carrier audio file (WAV or MP3 → outputs WAV)."""
    fname_lower = audio_file.filename.lower()
    if not (fname_lower.endswith(".wav") or fname_lower.endswith(".mp3")):
        raise HTTPException(status_code=400, detail="Audio carrier must be a WAV or MP3 file.")

    # 1. Read payload
    is_file = (payload_type == "file")
    payload_name = "secret.txt"
    mime_type = "text/plain"

    if is_file:
        if not secret_file:
            raise HTTPException(status_code=400, detail="Secret file is required when payload_type is 'file'.")
        raw_payload = await secret_file.read()
        payload_name = secret_file.filename
        mime_type = secret_file.content_type or "application/octet-stream"
        if len(raw_payload) == 0:
            raise HTTPException(status_code=400, detail="The secret file to embed cannot be empty.")
    else:
        if not secret_text or not secret_text.strip():
            raise HTTPException(status_code=400, detail="Secret text cannot be empty.")
        raw_payload = secret_text.encode("utf-8")
        payload_name = "Text message"

    # 2. Save carrier audio (keep original extension so _ensure_wav can detect MP3)
    unique_id = uuid.uuid4().hex
    in_ext = ".mp3" if fname_lower.endswith(".mp3") else ".wav"
    input_audio_path = TEMP_DIR / f"in_{unique_id}{in_ext}"
    output_audio_path = TEMP_DIR / f"stego_{unique_id}.wav"

    try:
        audio_bytes = await audio_file.read()
        if len(audio_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Carrier audio file exceeds upload limit.")
        with open(input_audio_path, "wb") as f:
            f.write(audio_bytes)


        # 3. Perform embedding in worker thread
        result = await asyncio.to_thread(
            embed_audio_data,
            input_path=str(input_audio_path),
            output_path=str(output_audio_path),
            raw_payload=raw_payload,
            is_file=is_file,
            filename=payload_name if is_file else None,
            mime_type=mime_type if is_file else None,
            password=password.strip() if password else None,
            require_face_scan=require_face_scan,
            recipient_phone=recipient_phone.strip() if recipient_phone else None,
            sender_id=sender_id.strip() if sender_id else None
        )

        # Record operation
        stats_tracker.record_operation(
            op_type="embed",
            media_type="audio",
            payload_type=payload_type,
            payload_name=payload_name,
            media_name=audio_file.filename,
            file_size_bytes=os.path.getsize(output_audio_path),
            encrypted=bool(password or recipient_phone),
            success=True
        )

        return {
            "status": "success",
            "download_id": unique_id,
            "filename": f"stego_{Path(audio_file.filename).stem}.wav",
            "file_size": os.path.getsize(output_audio_path),
            "payload_size": len(raw_payload),
            "envelope_size": result["envelope_bytes"],
            "capacity_used_pct": result["capacity_used_percentage"],
            "max_capacity_bytes": result["max_capacity_bytes"],
            "is_encrypted": result["is_encrypted"],
            "require_recipient_verify": result["require_recipient_verify"],
            "recipient_phone_masked": result.get("recipient_phone_masked"),
            "sample_rate": result["sample_rate"],
            "channels": result["channels"]
        }

    except InsufficientCapacityError as e:
        stats_tracker.record_operation("embed", "audio", payload_type, payload_name, audio_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=400, detail=str(e))
    except (AudioStegoError, PayloadError) as e:
        stats_tracker.record_operation("embed", "audio", payload_type, payload_name, audio_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        stats_tracker.record_operation("embed", "audio", payload_type, payload_name, audio_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=500, detail=f"Unexpected error during audio embedding: {str(e)}")
    finally:
        cleanup_file(str(input_audio_path))

@router.get("/download/{download_id}")
async def download_audio_file(download_id: str, background_tasks: BackgroundTasks):
    """Downloads the generated steganographic audio WAV file."""
    file_path = TEMP_DIR / f"stego_{download_id}.wav"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested stego audio file not found or has expired.")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=f"stego_audio_{download_id[:8]}.wav"
    )

@router.post("/extract")
async def audio_extract(
    audio_file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    recipient_phone: Optional[str] = Form(None)
):
    """Extracts hidden payload from a stego audio WAV file (output of embedding)."""
    # Note: extracted stego files are always WAV; MP3 on extraction would destroy LSBs
    if not audio_file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Extraction requires the stego WAV file generated by the embedding step. MP3 encoding destroys LSB data — only upload the unmodified stego .wav output.")

    temp_path = TEMP_DIR / f"ext_{uuid.uuid4().hex}.wav"
    try:
        content = await audio_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Audio file exceeds upload limit.")
        with open(temp_path, "wb") as f:
            f.write(content)


        stego_data = await asyncio.to_thread(
            extract_audio_data,
            str(temp_path),
            password=password.strip() if password else None,
            recipient_phone=recipient_phone.strip() if recipient_phone else None
        )

        if stego_data.require_recipient_verify:
            raise HTTPException(
                status_code=403,
                detail="This carrier file is protected by Live Biometric Face Verification. Please unlock using the Biometric Face Scanner."
            )

        payload_name = stego_data.filename if stego_data.is_file else "Extracted text"
        stats_tracker.record_operation(
            op_type="extract",
            media_type="audio",
            payload_type="file" if stego_data.is_file else "text",
            payload_name=payload_name,
            media_name=audio_file.filename,
            file_size_bytes=len(stego_data.content),
            encrypted=stego_data.is_encrypted,
            success=True
        )

        if stego_data.is_file:
            b64_content = base64.b64encode(stego_data.content).decode("utf-8")
            return {
                "status": "success",
                "is_file": True,
                "filename": stego_data.filename or "extracted_file.bin",
                "mime_type": stego_data.mime_type or "application/octet-stream",
                "file_size": len(stego_data.content),
                "data_base64": b64_content,
                "is_encrypted": stego_data.is_encrypted
            }
        else:
            decoded_text = stego_data.content.decode("utf-8", errors="replace")
            return {
                "status": "success",
                "is_file": False,
                "text": decoded_text,
                "length": len(decoded_text),
                "is_encrypted": stego_data.is_encrypted
            }

    except InvalidPasswordError as e:
        stats_tracker.record_operation("extract", "audio", "unknown", "failed", audio_file.filename, 0, True, False)
        raise HTTPException(status_code=401, detail=str(e))
    except (AudioStegoError, PayloadError) as e:
        stats_tracker.record_operation("extract", "audio", "unknown", "failed", audio_file.filename, 0, bool(password), False)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        stats_tracker.record_operation("extract", "audio", "unknown", "failed", audio_file.filename, 0, bool(password), False)
        raise HTTPException(status_code=500, detail=f"Unexpected error during audio extraction: {str(e)}")
    finally:
        cleanup_file(str(temp_path))
