import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

TEMP_DIR = BASE_DIR / "temp_uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Maximum file upload size: 100 MB default
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 100 * 1024 * 1024))

# Allowable formats
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

# SMS Gateway Configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "").strip()
FAST2SMS_API_KEY = os.environ.get("FAST2SMS_API_KEY", "").strip()
TWOFACTOR_API_KEY = os.environ.get("TWOFACTOR_API_KEY", "").strip()
TEXTBEE_API_KEY = os.environ.get("TEXTBEE_API_KEY", "").strip()
TEXTBEE_DEVICE_ID = os.environ.get("TEXTBEE_DEVICE_ID", "").strip()
SMS_WEBHOOK_URL = os.environ.get("SMS_WEBHOOK_URL", "").strip()

# Detect FFmpeg binary location
def find_ffmpeg_executable() -> str:
    # 1. System PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    
    # 2. Check WinGet Gyan FFmpeg location
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_path = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        for p in winget_path.glob("**/ffmpeg.exe"):
            if p.is_file():
                return str(p)
                
    # 3. Fallback to "ffmpeg"
    return "ffmpeg"

FFMPEG_PATH = find_ffmpeg_executable()
