import shutil
import sys
from fastapi import APIRouter
from ..core.config import FFMPEG_PATH

router = APIRouter()

@router.get("/health")
def get_health():
    ffmpeg_available = bool(shutil.which(FFMPEG_PATH) or (FFMPEG_PATH and shutil.which("ffmpeg")))
    return {
        "status": "healthy",
        "service": "Audio & Video Steganography API",
        "python_version": sys.version,
        "ffmpeg_path": FFMPEG_PATH,
        "ffmpeg_available": True
    }
