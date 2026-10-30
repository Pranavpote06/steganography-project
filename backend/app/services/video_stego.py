import os
import cv2
import struct
import json
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from ..core.config import FFMPEG_PATH
from ..core.payload import (
    pack_payload,
    unpack_payload,
    inspect_header_info,
    mask_phone,
    normalize_phone,
    StegoData,
    HEADER_SIZE,
    HEADER_FORMAT,
    MAGIC,
    PayloadError
)
from ..core.security import InvalidPasswordError

class VideoStegoError(Exception):
    """Base exception for video steganography operations."""
    pass

class VideoInsufficientCapacityError(VideoStegoError):
    """Raised when the carrier video has insufficient pixel capacity for the payload."""
    pass

def bytes_to_bits(data: bytes) -> np.ndarray:
    """Converts bytes to 1D uint8 array of 0s and 1s."""
    byte_arr = np.frombuffer(data, dtype=np.uint8)
    return np.unpackbits(byte_arr)

def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Converts 1D uint8 array of 0s and 1s to bytes."""
    return np.packbits(bits).tobytes()

def has_audio_stream(video_path: str) -> bool:
    """Checks whether the input video file contains an audio stream."""
    cmd = [FFMPEG_PATH, "-i", video_path]
    try:
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, errors="replace")
        return "Audio:" in res.stderr
    except Exception:
        return False

def get_video_info(video_path: str) -> Dict[str, Any]:
    """Inspects a video file and computes its capacity."""
    if not os.path.exists(video_path):
        raise VideoStegoError("Video file does not exist.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise VideoStegoError("Unable to open video file.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if total_frames <= 0 or width <= 0 or height <= 0:
        raise VideoStegoError("Invalid video properties or empty video file.")

    pixels_per_frame = width * height * 3
    total_capacity_bits = pixels_per_frame * total_frames
    capacity_bytes = total_capacity_bits // 8
    duration_sec = total_frames / fps if fps > 0 else 0

    return {
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "duration_seconds": round(duration_sec, 2),
        "has_audio": has_audio_stream(video_path),
        "capacity_bytes": capacity_bytes,
        "capacity_kb": round(capacity_bytes / 1024, 2),
        "capacity_mb": round(capacity_bytes / (1024 * 1024), 2)
    }

def inspect_video_carrier(input_path: str) -> Dict[str, Any]:
    """Inspects video frames to detect stego signature and recipient requirements."""
    if not os.path.exists(input_path):
        raise VideoStegoError("Input video file not found.")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return {"has_stego": False}

    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        return {"has_stego": False}

    flat = frame.ravel()
    header_bits_needed = HEADER_SIZE * 8
    if flat.size < header_bits_needed:
        cap.release()
        return {"has_stego": False}

    header_sample_bits = flat[:header_bits_needed] & 1
    header_bytes = bits_to_bytes(header_sample_bits)

    if not header_bytes.startswith(MAGIC):
        cap.release()
        return {"has_stego": False}

    info = inspect_header_info(header_bytes)
    meta_len = info["meta_len"]
    total_meta_bits = (HEADER_SIZE + meta_len) * 8

    # Extract metadata block across frames if needed
    collected_bits = [flat[:min(flat.size, total_meta_bits)] & 1]
    bits_count = collected_bits[0].size

    while bits_count < total_meta_bits:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        flat_f = frame.ravel()
        needed = total_meta_bits - bits_count
        take = min(flat_f.size, needed)
        collected_bits.append(flat_f[:take] & 1)
        bits_count += take

    cap.release()

    if bits_count >= total_meta_bits:
        all_bits = np.concatenate(collected_bits)
        all_bytes = bits_to_bytes(all_bits)
        meta_bytes = all_bytes[HEADER_SIZE : HEADER_SIZE + meta_len]
        try:
            meta_dict = json.loads(meta_bytes.decode("utf-8"))
            stored_phone = meta_dict.get("recipient_phone")
            sender_id = meta_dict.get("sender_id")
            require_face_scan = meta_dict.get("require_face_scan", False) or info.get("require_recipient_verify", False)
            info["require_face_scan"] = bool(require_face_scan)
            info["has_recipient_verify"] = bool(require_face_scan or stored_phone)
            info["masked_phone"] = mask_phone(stored_phone) if stored_phone else None
            info["stored_phone"] = stored_phone
            info["sender_id"] = sender_id
            info["has_password"] = meta_dict.get("has_password", False)
        except Exception:
            pass

    info["has_stego"] = True
    return info

def embed_video_data(
    input_path: str,
    output_path: str,
    raw_payload: bytes,
    is_file: bool = False,
    filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    password: Optional[str] = None,
    require_face_scan: bool = False,
    recipient_phone: Optional[str] = None,
    sender_id: Optional[str] = None
) -> Dict[str, Any]:
    """Embeds payload into video frames with lossless encoding and biometric face verification."""
    if not os.path.exists(input_path):
        raise VideoStegoError("Input video file not found.")

    info = get_video_info(input_path)
    width = info["width"]
    height = info["height"]
    fps = info["fps"]
    total_frames = info["total_frames"]
    has_audio = info["has_audio"]

    packed_blob = pack_payload(
        raw_data=raw_payload,
        is_file=is_file,
        filename=filename,
        mime_type=mime_type,
        password=password,
        require_face_scan=require_face_scan,
        recipient_phone=recipient_phone,
        sender_id=sender_id
    )

    required_bytes = len(packed_blob)
    required_bits = required_bytes * 8
    total_capacity_bits = width * height * 3 * total_frames

    if required_bits > total_capacity_bits:
        raise VideoInsufficientCapacityError(
            f"Insufficient video capacity: payload requires {required_bytes} bytes, "
            f"but video can hold at most {total_capacity_bits // 8} bytes."
        )

    payload_bits = bytes_to_bits(packed_blob)
    bits_embedded = 0
    total_bits = len(payload_bits)

    # Optimize frames to encode:
    # Large or long carrier videos (e.g. 50s-10min) can take minutes and cause gateway timeouts.
    # We dynamically calculate frames needed for payload plus buffer (up to 8 seconds / ~200 frames).
    bits_per_frame = width * height * 3
    frames_needed_for_payload = int(np.ceil(total_bits / bits_per_frame)) if bits_per_frame > 0 else 1
    target_buffer_frames = int(fps * 8) # 8-second standard playable carrier
    max_frames_to_encode = min(
        total_frames,
        max(frames_needed_for_payload + int(fps * 2), target_buffer_frames)
    )
    # Ensure all frames needed for payload are strictly encoded
    max_frames_to_encode = min(total_frames, max(frames_needed_for_payload, max_frames_to_encode))
    target_duration_sec = round(max_frames_to_encode / fps, 2) if fps > 0 else 8.0

    temp_audio_file = None
    if has_audio:
        fd, temp_audio_file = tempfile.mkstemp(suffix=".aac")
        os.close(fd)
        audio_extract_cmd = [
            FFMPEG_PATH, "-y", "-i", input_path,
            "-t", str(target_duration_sec),
            "-vn", "-c:a", "copy", temp_audio_file
        ]
        res = subprocess.run(audio_extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res.returncode != 0 or os.path.getsize(temp_audio_file) < 512:
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            fd, temp_audio_file = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            subprocess.run([
                FFMPEG_PATH, "-y", "-i", input_path,
                "-t", str(target_duration_sec),
                "-vn", "-c:a", "pcm_s16le", temp_audio_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not os.path.exists(temp_audio_file) or os.path.getsize(temp_audio_file) < 512:
                if os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
                temp_audio_file = None

    ffmpeg_cmd = [
        FFMPEG_PATH, "-y",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-"
    ]

    if temp_audio_file and os.path.exists(temp_audio_file):
        ffmpeg_cmd.extend(["-i", temp_audio_file, "-map", "0:v:0", "-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k"])
    else:
        ffmpeg_cmd.extend(["-map", "0:v:0"])

    ffmpeg_cmd.extend([
        "-c:v", "libx264rgb",
        "-crf", "0",
        "-preset", "ultrafast",
        "-threads", "1",
        "-x264-params", "threads=1:lookahead=5:sliced-threads=0",
        "-movflags", "+faststart",
        output_path
    ])

    import gc
    gc.collect()

    cap = cv2.VideoCapture(input_path)
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    frames_written = 0

    try:
        while frames_written < max_frames_to_encode:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if bits_embedded < total_bits:
                flat_frame = frame.ravel()
                remaining_bits = total_bits - bits_embedded
                embed_count = min(flat_frame.size, remaining_bits)

                chunk = payload_bits[bits_embedded : bits_embedded + embed_count]
                flat_frame[:embed_count] = (flat_frame[:embed_count] & 0xFE) | chunk

                bits_embedded += embed_count
                frame = flat_frame.reshape(frame.shape)

            proc.stdin.write(frame.tobytes())
            frames_written += 1

        proc.stdin.close()
        stderr_output = proc.stderr.read()
        proc.wait()

        if proc.returncode != 0:
            raise VideoStegoError(f"FFmpeg encoding error: {stderr_output.decode('utf-8', errors='replace')}")

        if bits_embedded < total_bits:
            raise VideoInsufficientCapacityError("Failed to embed all secret bits into the video frames.")

    finally:
        cap.release()
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.remove(temp_audio_file)
            except Exception:
                pass

    # Verify
    try:
        verify_cap = cv2.VideoCapture(output_path)
        ret, first_frame = verify_cap.read()
        verify_cap.release()
        if not ret or first_frame is None:
            fsize = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            raise VideoStegoError(f"Generated video produced an empty first frame (output file size: {fsize} bytes, frames written: {frames_written}).")
        first_bits = (first_frame.ravel()[:HEADER_SIZE * 8]) & 1
        header_bytes = bits_to_bytes(first_bits)
        if not header_bytes.startswith(MAGIC):
            raise VideoStegoError("Verification failed: Magic signature not found in stego video.")
    except Exception as e:
        raise VideoStegoError(f"Video verification failed: {str(e)}")

    max_capacity_bytes = total_capacity_bits // 8
    capacity_used_pct = round((required_bytes / max_capacity_bytes) * 100, 2)

    return {
        "status": "success",
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": frames_written,
        "payload_bytes": len(raw_payload),
        "envelope_bytes": required_bytes,
        "max_capacity_bytes": max_capacity_bytes,
        "capacity_used_percentage": capacity_used_pct,
        "is_encrypted": bool(password or recipient_phone),
        "require_recipient_verify": bool(require_face_scan or recipient_phone),
        "require_face_scan": bool(require_face_scan or recipient_phone),
        "recipient_phone_masked": mask_phone(recipient_phone) if recipient_phone else None,
        "preserved_audio": bool(temp_audio_file)
    }

def extract_video_data(
    input_path: str,
    password: Optional[str] = None,
    recipient_phone: Optional[str] = None
) -> StegoData:
    """Extracts embedded payload from video frames with recipient verification."""
    if not os.path.exists(input_path):
        raise VideoStegoError("Input video file not found.")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise VideoStegoError("Could not open video file.")

    header_bits_needed = HEADER_SIZE * 8

    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        raise VideoStegoError("Video file contains no frames.")

    flat = frame.ravel()
    if flat.size < header_bits_needed:
        cap.release()
        raise VideoStegoError("Frame too small.")

    header_sample_bits = flat[:header_bits_needed] & 1
    header_bytes = bits_to_bytes(header_sample_bits)

    if not header_bytes.startswith(MAGIC):
        cap.release()
        raise VideoStegoError("No hidden steganography payload detected in this video.")

    magic, version, flags, checksum, meta_len, fn_len_v1, payload_len = struct.unpack_from(
        HEADER_FORMAT, header_bytes, 0
    )

    if version == 1:
        total_bytes_needed = HEADER_SIZE + meta_len + fn_len_v1 + payload_len
    else:
        total_bytes_needed = HEADER_SIZE + meta_len + payload_len

    total_bits_needed = total_bytes_needed * 8

    all_bits = np.empty(total_bits_needed, dtype=np.uint8)
    first_frame_take = min(flat.size, total_bits_needed)
    all_bits[:first_frame_take] = flat[:first_frame_take] & 1
    bits_collected_count = first_frame_take

    while bits_collected_count < total_bits_needed:
        ret, frame = cap.read()
        if not ret or frame is None:
            break
        flat_f = frame.ravel()
        needed = total_bits_needed - bits_collected_count
        take = min(flat_f.size, needed)
        all_bits[bits_collected_count : bits_collected_count + take] = flat_f[:take] & 1
        bits_collected_count += take

    cap.release()

    if bits_collected_count < total_bits_needed:
        raise VideoStegoError("Corrupted or incomplete steganographic video data.")

    packed_data = bits_to_bytes(all_bits)

    return unpack_payload(packed_data, password=password, recipient_phone=recipient_phone)
