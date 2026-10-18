import os
import time
import base64
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FACE_CAPTURES_DIR = BASE_DIR / "face_captures"
FACE_CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

class AuditService:
    def __init__(self):
        self._audit_logs: List[Dict[str, Any]] = []

    def record_access_attempt(
        self,
        carrier_filename: str,
        media_type: str,
        recipient_phone: str,
        sender_id: Optional[str] = None,
        status: str = "SUCCESS_UNLOCKED",
        face_base64: Optional[str] = None,
        payload_name: str = "Confidential Payload",
        payload_type: str = "text",
        ip_address: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """
        Records an access attempt, decodes and saves the webcam face capture,
        and adds an audit entry visible to the sender.
        """
        audit_id = f"audit_{int(time.time() * 1000)}"
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        face_filename = None
        face_image_url = None

        if face_base64:
            # Strip data URL prefix if present: data:image/jpeg;base64,...
            clean_b64 = re.sub(r"^data:image\/\w+;base64,", "", face_base64)
            try:
                img_bytes = base64.b64decode(clean_b64)
                face_filename = f"{audit_id}.jpg"
                file_path = FACE_CAPTURES_DIR / face_filename
                with open(file_path, "wb") as f:
                    f.write(img_bytes)
                face_image_url = f"/api/security/face/{audit_id}"
            except Exception as e:
                print(f"Failed to save face capture image: {e}")

        entry = {
            "id": audit_id,
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "carrier_filename": carrier_filename,
            "media_type": media_type,
            "recipient_phone": recipient_phone,
            "sender_id": sender_id or "Default-Sender",
            "status": status,
            "has_face_capture": bool(face_filename),
            "face_image_url": face_image_url,
            "face_filename": face_filename,
            "payload_name": payload_name,
            "payload_type": payload_type,
            "ip_address": ip_address
        }

        # Keep latest 50 records
        self._audit_logs.insert(0, entry)
        if len(self._audit_logs) > 50:
            self._audit_logs.pop()

        return entry

    def get_audit_logs(self, sender_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns access audit logs, optionally filtered by sender."""
        if not sender_id:
            return self._audit_logs
        return [log for log in self._audit_logs if log.get("sender_id") == sender_id]

    def get_face_image_path(self, audit_id: str) -> Optional[Path]:
        """Resolves the file path of a captured face image."""
        file_path = FACE_CAPTURES_DIR / f"{audit_id}.jpg"
        if file_path.exists():
            return file_path
        return None

    def clear_logs(self):
        """Clears audit logs and purged capture images."""
        self._audit_logs.clear()
        for f in FACE_CAPTURES_DIR.glob("*.jpg"):
            try:
                f.unlink()
            except Exception:
                pass

audit_service = AuditService()
