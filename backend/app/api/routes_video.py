import os
import uuid
import base64
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from ..core.config import TEMP_DIR, MAX_UPLOAD_SIZE, ALLOWED_VIDEO_EXTENSIONS
from ..services.video_stego import (
    embed_video_data,
    extract_video_data,
    get_video_info,
    VideoStegoError,
    VideoInsufficientCapacityError
)
from ..core.security import InvalidPasswordError
from ..core.payload import PayloadError
from ..services.stats_service import stats_tracker

router = APIRouter()

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@router.post("/capacity")
async def video_capacity(video_file: UploadFile = File(...)):
    """Inspects a video file and calculates its steganographic capacity."""
    ext = Path(video_file.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed video extensions are: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    temp_path = TEMP_DIR / f"cap_vid_{uuid.uuid4().hex}{ext}"
    try:
        content = await video_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum upload size of {MAX_UPLOAD_SIZE // (1024*1024)}MB.")
        with open(temp_path, "wb") as f:
            f.write(content)

        info = get_video_info(str(temp_path))
        info["filename"] = video_file.filename
        info["file_size_bytes"] = len(content)
        return info
    except VideoStegoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect video: {str(e)}")
    finally:
        cleanup_file(str(temp_path))

@router.post("/embed")
async def video_embed(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    payload_type: str = Form(...), # "text" or "file"
    secret_text: Optional[str] = Form(None),
    secret_file: Optional[UploadFile] = File(None),
    password: Optional[str] = Form(None),
    require_face_scan: bool = Form(False),
    recipient_phone: Optional[str] = Form(None),
    sender_id: Optional[str] = Form(None)
):
    """Embeds confidential text or file into a carrier video."""
    ext = Path(video_file.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Allowed formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

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

    # 2. Save carrier video
    unique_id = uuid.uuid4().hex
    input_video_path = TEMP_DIR / f"in_vid_{unique_id}{ext}"
    output_video_path = TEMP_DIR / f"stego_{unique_id}.mp4"

    try:
        video_bytes = await video_file.read()
        if len(video_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Carrier video file exceeds upload limit.")
        with open(input_video_path, "wb") as f:
            f.write(video_bytes)

        # 3. Perform embedding
        result = embed_video_data(
            input_path=str(input_video_path),
            output_path=str(output_video_path),
            raw_payload=raw_payload,
            is_file=is_file,
            filename=payload_name if is_file else None,
            mime_type=mime_type if is_file else None,
            password=password.strip() if password else None,
            require_face_scan=require_face_scan,
            recipient_phone=recipient_phone.strip() if recipient_phone else None,
            sender_id=sender_id.strip() if sender_id else None
        )

        stats_tracker.record_operation(
            op_type="embed",
            media_type="video",
            payload_type=payload_type,
            payload_name=payload_name,
            media_name=video_file.filename,
            file_size_bytes=os.path.getsize(output_video_path),
            encrypted=bool(password or recipient_phone),
            success=True
        )

        return {
            "status": "success",
            "download_id": unique_id,
            "filename": f"stego_{Path(video_file.filename).stem}.mp4",
            "file_size": os.path.getsize(output_video_path),
            "payload_size": len(raw_payload),
            "envelope_size": result["envelope_bytes"],
            "capacity_used_pct": result["capacity_used_percentage"],
            "max_capacity_bytes": result["max_capacity_bytes"],
            "is_encrypted": result["is_encrypted"],
            "require_recipient_verify": result["require_recipient_verify"],
            "recipient_phone_masked": result.get("recipient_phone_masked"),
            "preserved_audio": result["preserved_audio"],
            "resolution": f"{result['width']}x{result['height']}",
            "fps": result["fps"],
            "frames": result["total_frames"]
        }

    except VideoInsufficientCapacityError as e:
        stats_tracker.record_operation("embed", "video", payload_type, payload_name, video_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=400, detail=str(e))
    except (VideoStegoError, PayloadError) as e:
        stats_tracker.record_operation("embed", "video", payload_type, payload_name, video_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        stats_tracker.record_operation("embed", "video", payload_type, payload_name, video_file.filename, 0, bool(password or recipient_phone), False)
        raise HTTPException(status_code=500, detail=f"Unexpected error during video embedding: {str(e)}")
    finally:
        cleanup_file(str(input_video_path))

@router.get("/download/{download_id}")
async def download_video_file(download_id: str):
    """Downloads the generated steganographic MP4 video file."""
    file_path = TEMP_DIR / f"stego_{download_id}.mp4"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested stego video file not found or has expired.")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=f"stego_video_{download_id[:8]}.mp4"
    )

@router.post("/extract")
async def video_extract(
    video_file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    recipient_phone: Optional[str] = Form(None)
):
    """Extracts hidden payload from a steganographic video."""
    ext = Path(video_file.filename).suffix.lower()
    temp_path = TEMP_DIR / f"ext_vid_{uuid.uuid4().hex}{ext}"
    try:
        content = await video_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Video file exceeds upload limit.")
        with open(temp_path, "wb") as f:
            f.write(content)

        stego_data = extract_video_data(
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
            media_type="video",
            payload_type="file" if stego_data.is_file else "text",
            payload_name=payload_name,
            media_name=video_file.filename,
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
        stats_tracker.record_operation("extract", "video", "unknown", "failed", video_file.filename, 0, True, False)
        raise HTTPException(status_code=401, detail=str(e))
    except (VideoStegoError, PayloadError) as e:
        stats_tracker.record_operation("extract", "video", "unknown", "failed", video_file.filename, 0, bool(password), False)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        stats_tracker.record_operation("extract", "video", "unknown", "failed", video_file.filename, 0, bool(password), False)
        raise HTTPException(status_code=500, detail=f"Unexpected error during video extraction: {str(e)}")
    finally:
        cleanup_file(str(temp_path))
