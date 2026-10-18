import time
from typing import List, Dict, Any

class StatsService:
    def __init__(self):
        self.audio_embed_count = 0
        self.audio_extract_count = 0
        self.video_embed_count = 0
        self.video_extract_count = 0
        self.recent_operations: List[Dict[str, Any]] = []

    def record_operation(
        self,
        op_type: str,     # "embed" or "extract"
        media_type: str,  # "audio" or "video"
        payload_type: str,# "text" or "file"
        payload_name: str,
        media_name: str,
        file_size_bytes: int,
        encrypted: bool,
        success: bool = True
    ):
        if media_type == "audio":
            if op_type == "embed":
                self.audio_embed_count += 1
            else:
                self.audio_extract_count += 1
        elif media_type == "video":
            if op_type == "embed":
                self.video_embed_count += 1
            else:
                self.video_extract_count += 1

        op_entry = {
            "id": f"op_{int(time.time() * 1000)}",
            "timestamp": time.time(),
            "op_type": op_type,
            "media_type": media_type,
            "payload_type": payload_type,
            "payload_name": payload_name,
            "media_name": media_name,
            "file_size_bytes": file_size_bytes,
            "encrypted": encrypted,
            "success": success
        }
        # Keep latest 25 operations
        self.recent_operations.insert(0, op_entry)
        if len(self.recent_operations) > 25:
            self.recent_operations.pop()

    def get_stats(self) -> Dict[str, Any]:
        total_audio = self.audio_embed_count + self.audio_extract_count
        total_video = self.video_embed_count + self.video_extract_count
        total_ops = total_audio + total_video
        return {
            "total_processed": total_ops,
            "audio_processed": total_audio,
            "video_processed": total_video,
            "audio_embeds": self.audio_embed_count,
            "audio_extracts": self.audio_extract_count,
            "video_embeds": self.video_embed_count,
            "video_extracts": self.video_extract_count,
            "recent_operations": self.recent_operations
        }

    def reset_stats(self):
        self.audio_embed_count = 0
        self.audio_extract_count = 0
        self.video_embed_count = 0
        self.video_extract_count = 0
        self.recent_operations.clear()

stats_tracker = StatsService()
