import os
import struct
import json
import subprocess
import tempfile
import shutil
import numpy as np
import scipy.io.wavfile as wavfile
import soundfile as sf
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

class AudioStegoError(Exception):
    """Base exception for audio steganography operations."""
    pass

class InsufficientCapacityError(AudioStegoError):
    """Raised when the carrier audio does not have enough capacity for the payload."""
    pass

def convert_to_wav(input_path: str, output_path: str) -> None:
    """Converts any audio format (e.g. MP3) to uncompressed PCM WAV using FFmpeg."""
    try:
        result = subprocess.run(
            [FFMPEG_PATH, "-y", "-i", input_path, "-ar", "44100", "-ac", "2",
             "-acodec", "pcm_s16le", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )
        if result.returncode != 0:
            raise AudioStegoError(
                f"FFmpeg failed to convert audio: {result.stderr.decode('utf-8', errors='replace')[-400:]}"
            )
    except subprocess.TimeoutExpired:
        raise AudioStegoError("Audio conversion timed out.")
    except FileNotFoundError:
        raise AudioStegoError("FFmpeg not found. Cannot convert MP3 to WAV.")

def _ensure_wav(input_path: str) -> tuple[str, bool]:
    """
    Returns (wav_path, is_tmp).
    If input is already WAV, returns (input_path, False).
    Otherwise converts to a temporary WAV and returns (tmp_path, True).
    """
    if input_path.lower().endswith(".wav"):
        return input_path, False
    suffix = Path(input_path).suffix.lower()
    tmp_wav = tempfile.mktemp(suffix="_converted.wav")
    convert_to_wav(input_path, tmp_wav)
    return tmp_wav, True


def bytes_to_bits(data: bytes) -> np.ndarray:
    """Converts a bytes buffer into a 1D NumPy array of bits."""
    byte_arr = np.frombuffer(data, dtype=np.uint8)
    return np.unpackbits(byte_arr)

def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Converts a 1D NumPy array of bits into bytes."""
    return np.packbits(bits).tobytes()

def get_audio_info(file_path: str) -> Dict[str, Any]:
    """Inspects an audio file (WAV or MP3) and calculates its steganographic capacity."""
    wav_path, is_tmp = _ensure_wav(file_path)
    try:
        info = sf.info(wav_path)
        sample_rate = info.samplerate
        channels = info.channels
        frames = info.frames
        duration = info.duration
        subtype = info.subtype
        format_name = info.format

        total_samples = frames * channels
        capacity_bytes = total_samples // 8

        is_mp3_input = not file_path.lower().endswith(".wav")
        return {
            "format": "MP3 → WAV (lossless re-encode)" if is_mp3_input else format_name,
            "subtype": subtype,
            "sample_rate": sample_rate,
            "channels": channels,
            "frames": frames,
            "duration_seconds": round(duration, 2),
            "total_samples": total_samples,
            "capacity_bytes": capacity_bytes,
            "capacity_kb": round(capacity_bytes / 1024, 2),
            "is_mp3_input": is_mp3_input,
        }
    except Exception as e:
        raise AudioStegoError(f"Failed to inspect audio file: {str(e)}")
    finally:
        if is_tmp and os.path.exists(wav_path):
            os.remove(wav_path)


def inspect_audio_carrier(input_path: str) -> Dict[str, Any]:
    """Inspects an audio file to determine if it has stego data and what security it requires."""
    if not os.path.exists(input_path):
        raise AudioStegoError("Carrier audio file not found.")

    wav_path, is_tmp = _ensure_wav(input_path)
    try:
        try:
            sample_rate, data = wavfile.read(wav_path)
        except Exception:
            try:
                data, sample_rate = sf.read(wav_path, dtype='int16')
            except Exception as e:
                raise AudioStegoError(f"Could not read audio file: {str(e)}")

        flat_samples = data.ravel()
        header_bits_needed = HEADER_SIZE * 8
        if flat_samples.size < header_bits_needed:
            return {"has_stego": False, "error": "File too small"}

        header_sample_bits = flat_samples[:header_bits_needed] & 1
        header_bytes = bits_to_bytes(header_sample_bits)

        if not header_bytes.startswith(MAGIC):
            return {"has_stego": False}

        info = inspect_header_info(header_bytes)
        meta_len = info["meta_len"]

        # Extract metadata block to check phone and sender
        total_meta_bits = (HEADER_SIZE + meta_len) * 8
        if flat_samples.size >= total_meta_bits:
            all_meta_bits = flat_samples[:total_meta_bits] & 1
            meta_bytes = bits_to_bytes(all_meta_bits)[HEADER_SIZE : HEADER_SIZE + meta_len]
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
    finally:
        if is_tmp and os.path.exists(wav_path):
            os.remove(wav_path)


def embed_audio_data(
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
    """
    Embeds raw_payload into an audio carrier using 1-bit LSB.
    Accepts WAV or MP3 input (MP3 is losslessly converted to WAV first).
    Output is always lossless PCM WAV so embedded bits are preserved exactly.
    Supports live biometric face verification and sender tracking.
    """
    if not os.path.exists(input_path):
        raise AudioStegoError("Input audio file not found.")

    wav_path, is_tmp = _ensure_wav(input_path)
    try:
        try:
            sample_rate, data = wavfile.read(wav_path)
        except Exception:
            try:
                data, sample_rate = sf.read(wav_path, dtype='int16')
            except Exception as e:
                raise AudioStegoError(f"Unsupported audio format: {str(e)}")

        if data.dtype == np.int16:
            audio_array = data.copy()
        elif data.dtype == np.uint8:
            audio_array = data.copy()
        elif data.dtype in (np.float32, np.float64):
            audio_array = (data * 32767.0).clip(-32768, 32767).astype(np.int16)
        elif data.dtype == np.int32:
            audio_array = (data >> 16).astype(np.int16)
        else:
            audio_array = data.astype(np.int16)

        orig_shape = audio_array.shape
        flat_samples = audio_array.ravel()
        total_samples = flat_samples.size
        max_capacity_bytes = total_samples // 8

        # Pack payload
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

        if required_bits > total_samples:
            raise InsufficientCapacityError(
                f"Insufficient audio capacity: payload requires {required_bytes} bytes "
                f"({required_bytes / 1024:.2f} KB), but audio capacity is {max_capacity_bytes} bytes. "
                f"Please use a longer audio carrier."
            )

        payload_bits = bytes_to_bits(packed_blob)
        bit_slice = payload_bits.astype(flat_samples.dtype)
        flat_samples[:required_bits] = (flat_samples[:required_bits] & ~1) | bit_slice

        stego_audio = flat_samples.reshape(orig_shape)
        wavfile.write(output_path, sample_rate, stego_audio)

        capacity_used_pct = round((required_bytes / max_capacity_bytes) * 100, 2)

        return {
            "status": "success",
            "sample_rate": sample_rate,
            "channels": 1 if len(orig_shape) == 1 else orig_shape[1],
            "total_samples": total_samples,
            "payload_bytes": len(raw_payload),
            "envelope_bytes": required_bytes,
            "max_capacity_bytes": max_capacity_bytes,
            "capacity_used_percentage": capacity_used_pct,
            "is_encrypted": bool(password or recipient_phone),
            "require_recipient_verify": bool(require_face_scan or recipient_phone),
            "require_face_scan": bool(require_face_scan or recipient_phone),
            "recipient_phone_masked": mask_phone(recipient_phone) if recipient_phone else None
        }
    finally:
        if is_tmp and os.path.exists(wav_path):
            os.remove(wav_path)


def extract_audio_data(
    input_path: str,
    password: Optional[str] = None,
    recipient_phone: Optional[str] = None
) -> StegoData:
    """Extracts embedded payload from an audio WAV file."""
    if not os.path.exists(input_path):
        raise AudioStegoError("Input audio file not found.")

    try:
        sample_rate, data = wavfile.read(input_path)
    except Exception:
        try:
            data, sample_rate = sf.read(input_path, dtype='int16')
        except Exception as e:
            raise AudioStegoError(f"Could not read audio file: {str(e)}")

    flat_samples = data.ravel()
    total_samples = flat_samples.size

    header_bits_needed = HEADER_SIZE * 8
    if total_samples < header_bits_needed:
        raise AudioStegoError("Audio file is too short to contain steganographic data.")

    header_sample_bits = flat_samples[:header_bits_needed] & 1
    header_bytes = bits_to_bytes(header_sample_bits)

    if not header_bytes.startswith(MAGIC):
        raise AudioStegoError(
            "No hidden steganography payload detected. Magic signature was missing or carrier audio has been modified."
        )

    magic, version, flags, checksum, meta_len, fn_len_v1, payload_len = struct.unpack_from(
        HEADER_FORMAT, header_bytes, 0
    )

    if version == 1:
        total_bytes_needed = HEADER_SIZE + meta_len + fn_len_v1 + payload_len
    else:
        total_bytes_needed = HEADER_SIZE + meta_len + payload_len

    total_bits_needed = total_bytes_needed * 8

    if total_bits_needed > total_samples:
        raise AudioStegoError("Corrupted or incomplete steganographic data in audio.")

    all_sample_bits = flat_samples[:total_bits_needed] & 1
    packed_data = bits_to_bytes(all_sample_bits)

    return unpack_payload(packed_data, password=password, recipient_phone=recipient_phone)
