import struct
import zlib
import json
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from .security import encrypt_payload, decrypt_payload, InvalidPasswordError

MAGIC = b"STEG"
VERSION = 2  # Version 2 with extended metadata and recipient verification support

FLAG_ENCRYPTED = 0x01
FLAG_IS_FILE = 0x02
FLAG_RECIPIENT_VERIFY = 0x04

# Fixed header format (18 bytes):
# MAGIC (4s) + VERSION (B) + FLAGS (B) + CRC32 (I) + META_LEN (H) + UNUSED (H) + PAYLOAD_LEN (I)
HEADER_FORMAT = ">4sBBIHHI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) # 18 bytes

class PayloadError(Exception):
    """Raised for malformed, corrupted or invalid payload structures."""
    pass

@dataclass
class StegoData:
    content: bytes
    is_file: bool
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    is_encrypted: bool = False
    recipient_phone: Optional[str] = None
    sender_id: Optional[str] = None
    require_recipient_verify: bool = False

def normalize_phone(phone: Optional[str]) -> str:
    """Strips all non-digit characters except leading plus."""
    if not phone:
        return ""
    clean = re.sub(r"[^\d+]", "", phone.strip())
    # Keep only digits or +
    return clean

def mask_phone(phone: Optional[str]) -> str:
    """Masks a phone number for privacy display (e.g., +1 (***) ***-1234)."""
    if not phone:
        return "Unknown"
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "****"
    return f"+{'*' * (len(digits) - 4)}{digits[-4:]}"

def pack_payload(
    raw_data: bytes,
    is_file: bool = False,
    filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    password: Optional[str] = None,
    require_face_scan: bool = False,
    recipient_phone: Optional[str] = None,
    sender_id: Optional[str] = None
) -> bytes:
    """
    Packs data into the secure binary envelope with magic signature, CRC32,
    metadata JSON (filename, mime, require_face_scan, sender), and optional AES-256-GCM encryption.
    """
    flags = 0
    if is_file:
        flags |= FLAG_IS_FILE

    norm_phone = normalize_phone(recipient_phone)
    if require_face_scan or norm_phone:
        flags |= FLAG_RECIPIENT_VERIFY

    # Key derivation material:
    encryption_key = None
    if password or norm_phone:
        flags |= FLAG_ENCRYPTED
        if password and norm_phone:
            # Legacy combined key (phone + password)
            encryption_key = f"{password}:{norm_phone}"
        elif password:
            # Password-only (new face-scan flow)
            encryption_key = password
        else:
            # Phone-only (no password)
            encryption_key = f"SECURE_RECIPIENT_KEY:{norm_phone}"

    payload_bytes = raw_data
    if encryption_key:
        payload_bytes = encrypt_payload(raw_data, encryption_key)

    checksum = zlib.crc32(payload_bytes) & 0xFFFFFFFF

    # Metadata JSON block
    meta_dict = {
        "is_file": is_file,
        "filename": filename if is_file else None,
        "mime_type": mime_type if is_file else None,
        "require_face_scan": bool(require_face_scan or norm_phone),
        "recipient_phone": norm_phone if norm_phone else None,
        "sender_id": sender_id if sender_id else None,
        "has_password": bool(password)
    }
    meta_bytes = json.dumps(meta_dict).encode("utf-8")

    if len(meta_bytes) > 65535:
        raise PayloadError("Metadata block exceeds maximum allowed length.")

    header = struct.pack(
        HEADER_FORMAT,
        MAGIC,
        VERSION,
        flags,
        checksum,
        len(meta_bytes),
        0, # Reserved / unused
        len(payload_bytes)
    )

    return header + meta_bytes + payload_bytes

def inspect_header_info(packed_header_bytes: bytes) -> Dict[str, Any]:
    """Inspects header bytes without decrypting the payload."""
    if len(packed_header_bytes) < HEADER_SIZE:
        raise PayloadError("Data is too short to contain a valid steganography header.")

    magic, version, flags, checksum, meta_len, _, payload_len = struct.unpack_from(
        HEADER_FORMAT, packed_header_bytes, 0
    )

    if magic != MAGIC:
        raise PayloadError("Invalid steganography signature (Magic bytes do not match).")

    is_encrypted = bool(flags & FLAG_ENCRYPTED)
    is_file = bool(flags & FLAG_IS_FILE)
    require_recipient_verify = bool(flags & FLAG_RECIPIENT_VERIFY)

    return {
        "magic": magic.decode("latin1"),
        "version": version,
        "is_encrypted": is_encrypted,
        "is_file": is_file,
        "require_recipient_verify": require_recipient_verify,
        "meta_len": meta_len,
        "payload_len": payload_len,
        "total_expected_size": HEADER_SIZE + meta_len + payload_len
    }

def unpack_payload(
    packed_data: bytes,
    password: Optional[str] = None,
    recipient_phone: Optional[str] = None
) -> StegoData:
    """
    Unpacks and validates the binary envelope.
    Verifies magic signature, CRC32 integrity, recipient phone, and decrypts payload.
    """
    if len(packed_data) < HEADER_SIZE:
        raise PayloadError("Data is too short to contain a valid steganography header.")

    magic, version, flags, checksum, meta_len, fn_len_v1, payload_len = struct.unpack_from(
        HEADER_FORMAT, packed_data, 0
    )

    if magic != MAGIC:
        raise PayloadError("Invalid steganography signature (Magic bytes do not match).")

    is_encrypted = bool(flags & FLAG_ENCRYPTED)
    is_file = bool(flags & FLAG_IS_FILE)
    require_recipient_verify = bool(flags & FLAG_RECIPIENT_VERIFY)

    # Support Version 1 legacy format backward compatibility
    if version == 1:
        total_expected_len = HEADER_SIZE + meta_len + fn_len_v1 + payload_len
        if len(packed_data) < total_expected_len:
            raise PayloadError(f"Truncated data: expected {total_expected_len} bytes, found {len(packed_data)} bytes.")

        offset = HEADER_SIZE
        mime_bytes = packed_data[offset : offset + meta_len]
        offset += meta_len
        fn_bytes = packed_data[offset : offset + fn_len_v1]
        offset += fn_len_v1
        payload_bytes = packed_data[offset : offset + payload_len]

        computed_crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF
        if computed_crc != checksum:
            raise PayloadError("Payload integrity check failed (CRC32 mismatch). Media may have been modified.")

        if is_encrypted:
            if not password:
                raise InvalidPasswordError("This hidden payload is encrypted with a password.")
            final_bytes = decrypt_payload(payload_bytes, password)
        else:
            final_bytes = payload_bytes

        return StegoData(
            content=final_bytes,
            is_file=is_file,
            filename=fn_bytes.decode("utf-8", errors="replace") if is_file and fn_bytes else None,
            mime_type=mime_bytes.decode("utf-8", errors="replace") if is_file and mime_bytes else None,
            is_encrypted=is_encrypted
        )

    # Version 2 format
    total_expected_len = HEADER_SIZE + meta_len + payload_len
    if len(packed_data) < total_expected_len:
        raise PayloadError(f"Corrupted or truncated data: expected {total_expected_len} bytes, but found {len(packed_data)} bytes.")

    offset = HEADER_SIZE
    meta_bytes = packed_data[offset : offset + meta_len]
    offset += meta_len
    payload_bytes = packed_data[offset : offset + payload_len]

    # Verify CRC32 integrity before anything else
    computed_crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF
    if computed_crc != checksum:
        raise PayloadError("Payload integrity check failed (CRC32 mismatch). Carrier media may have been altered or compressed.")

    # Parse metadata
    try:
        meta_dict = json.loads(meta_bytes.decode("utf-8"))
    except Exception as e:
        raise PayloadError(f"Malformed envelope metadata: {str(e)}")

    stored_phone = meta_dict.get("recipient_phone")
    sender_id = meta_dict.get("sender_id")
    has_password = meta_dict.get("has_password", False)
    filename = meta_dict.get("filename")
    mime_type = meta_dict.get("mime_type")

    # If recipient verification is required, check phone number
    if require_recipient_verify and stored_phone:
        if not recipient_phone:
            raise InvalidPasswordError("This file is protected by Recipient Phone & Face Scan Verification. Phone number is required.")
        norm_input_phone = normalize_phone(recipient_phone)
        norm_stored_phone = normalize_phone(stored_phone)
        # Match either exact or last 10 digits
        if norm_input_phone != norm_stored_phone and norm_input_phone[-10:] != norm_stored_phone[-10:]:
            raise InvalidPasswordError("Access Denied: The provided phone number is not authorized to unlock this confidential file.")

    # Decrypt if encrypted
    if is_encrypted:
        norm_phone = normalize_phone(stored_phone or recipient_phone)
        if has_password and password and norm_phone:
            # Legacy: password + phone combined key
            decryption_key = f"{password}:{norm_phone}"
        elif has_password and password:
            # New flow: password only (face scan replaces phone)
            decryption_key = password
        elif norm_phone:
            # Phone-only key (no password set)
            decryption_key = f"SECURE_RECIPIENT_KEY:{norm_phone}"
        else:
            raise InvalidPasswordError("Authentication credentials required to decrypt payload.")

        final_bytes = decrypt_payload(payload_bytes, decryption_key)
    else:
        final_bytes = payload_bytes

    return StegoData(
        content=final_bytes,
        is_file=is_file,
        filename=filename,
        mime_type=mime_type,
        is_encrypted=is_encrypted,
        recipient_phone=stored_phone,
        sender_id=sender_id,
        require_recipient_verify=require_recipient_verify
    )
