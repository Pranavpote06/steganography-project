import os
import pytest
import cv2
import numpy as np
import subprocess
from app.core.config import FFMPEG_PATH
from app.services.video_stego import (
    embed_video_data,
    extract_video_data,
    get_video_info,
    VideoStegoError,
    VideoInsufficientCapacityError
)
from app.core.security import InvalidPasswordError

@pytest.fixture
def sample_video(tmp_path):
    """Generates a synthetic 1-second 160x120 24fps MP4 video."""
    width, height, fps, num_frames = 160, 120, 24, 24
    video_path = str(tmp_path / "carrier.mp4")
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264rgb",
        "-crf", "0",
        "-preset", "ultrafast",
        video_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(num_frames):
        # Create patterned colorful frame
        frame = np.full((height, width, 3), (i * 10) % 255, dtype=np.uint8)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    
    return video_path

def test_video_embed_extract_text(sample_video, tmp_path):
    output_video = str(tmp_path / "stego_video_text.mp4")
    secret_text = "PROJECT_AEGIS: Stealth transmission verified."
    
    res = embed_video_data(
        input_path=sample_video,
        output_path=output_video,
        raw_payload=secret_text.encode("utf-8"),
        is_file=False
    )
    assert res["status"] == "success"
    assert res["payload_bytes"] == len(secret_text.encode("utf-8"))
    
    recovered = extract_video_data(output_video)
    assert not recovered.is_file
    assert recovered.content.decode("utf-8") == secret_text

def test_video_embed_extract_file_encrypted(sample_video, tmp_path):
    output_video = str(tmp_path / "stego_video_file.mp4")
    file_bytes = b"BINARY_PAYLOAD_ARCHIVE_DATA_PK\x03\x04_MOCK_ZIP_CONTENT"
    password = "VideoKeyOmega99"
    
    embed_video_data(
        input_path=sample_video,
        output_path=output_video,
        raw_payload=file_bytes,
        is_file=True,
        filename="archive.zip",
        mime_type="application/zip",
        password=password
    )
    
    # Missing password
    with pytest.raises(InvalidPasswordError):
        extract_video_data(output_video, password=None)
        
    # Wrong password
    with pytest.raises(InvalidPasswordError):
        extract_video_data(output_video, password="WrongVideoPassword")
        
    # Correct password
    recovered = extract_video_data(output_video, password=password)
    assert recovered.is_file
    assert recovered.filename == "archive.zip"
    assert recovered.mime_type == "application/zip"
    assert recovered.content == file_bytes

def test_video_no_stego_detected(sample_video):
    with pytest.raises(VideoStegoError, match="No hidden steganography payload detected"):
        extract_video_data(sample_video)

def test_video_get_info(sample_video):
    info = get_video_info(sample_video)
    assert info["width"] == 160
    assert info["height"] == 120
    assert info["fps"] == 24.0
    assert info["capacity_bytes"] > 0
