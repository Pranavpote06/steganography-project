import os
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

SAMPLE_DIR = Path("sample_media")
SAMPLE_DIR.mkdir(exist_ok=True)

# 1. Create Sample WAV Audio (3 seconds, 44100 Hz, 16-bit PCM stereo)
sample_rate = 44100
duration = 3.0
num_samples = int(sample_rate * duration)
t = np.linspace(0, duration, num_samples, False)

# Compose pleasant chord (440Hz A4 + 554.37Hz C#5 + 659.25Hz E5)
tone_a = np.sin(2 * np.pi * 440.0 * t)
tone_c = np.sin(2 * np.pi * 554.37 * t)
tone_e = np.sin(2 * np.pi * 659.25 * t)
chord = (tone_a + tone_c + tone_e) / 3.0

# Apply gentle fade-in and fade-out
fade_len = int(sample_rate * 0.1)
fade = np.linspace(0, 1, fade_len)
envelope = np.ones(num_samples)
envelope[:fade_len] = fade
envelope[-fade_len:] = fade[::-1]

chord = chord * envelope
audio_int16 = (chord * 20000).astype(np.int16)
stereo_audio = np.column_stack((audio_int16, audio_int16))

wav_path = SAMPLE_DIR / "sample_audio.wav"
wavfile.write(str(wav_path), sample_rate, stereo_audio)
print(f"Created sample audio: {wav_path} ({os.path.getsize(wav_path)} bytes, capacity: {num_samples * 2 // 8} bytes)")

# 2. Create Sample MP4 Video (2 seconds, 320x240, 24 fps) using FFmpeg
mp4_path = SAMPLE_DIR / "sample_video.mp4"
from backend.app.core.config import FFMPEG_PATH

cmd = [
    FFMPEG_PATH, "-y",
    "-f", "lavfi",
    "-i", "testsrc=size=320x240:rate=24:duration=2",
    "-f", "lavfi",
    "-i", "sine=frequency=440:duration=2",
    "-c:v", "libx264rgb",
    "-crf", "0",
    "-preset", "ultrafast",
    "-c:a", "aac",
    str(mp4_path)
]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if mp4_path.exists():
    print(f"Created sample video: {mp4_path} ({os.path.getsize(mp4_path)} bytes)")

# 3. Create Sample Secret Text File
secret_txt = SAMPLE_DIR / "secret_intel.txt"
with open(secret_txt, "w", encoding="utf-8") as f:
    f.write("TOP SECRET CYBER INTELLIGENCE REPORT\n")
    f.write("Timestamp: 2026-10-17 14:00 UTC\n")
    f.write("Operation: PROJECT_PHANTOM\n")
    f.write("Coordinates: 40.7128N, 74.0060W\n")
    f.write("Status: Stealth transmission verified via LSB Steganography.\n")
print(f"Created secret text: {secret_txt}")

# 4. Create Sample Secret PDF File (minimal valid PDF)
pdf_content = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"
)
secret_pdf = SAMPLE_DIR / "secret_document.pdf"
with open(secret_pdf, "wb") as f:
    f.write(pdf_content)
print(f"Created secret PDF: {secret_pdf}")
