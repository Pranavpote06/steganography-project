# StegoCyber: Audio and Video Steganography Web Application

**StegoCyber** is a full-stack cybersecurity educational platform demonstrating digital media steganography and defense-in-depth authenticated encryption. It enables users to imperceptibly conceal confidential text messages or arbitrary binary files inside audio waveforms (WAV) and video frames (MP4/AVI), and recover them using a unified extraction interface.

---

## 1. Key Features

- **Text-to-Audio Steganography**: 1-bit LSB substitution across uncompressed 16-bit PCM WAV samples with ~-96 dB SNR impact (inaudible distortion).
- **File-to-Audio Steganography**: Embeds arbitrary binary files (PDF, DOCX, ZIP, PNG, JPG, TXT) while preserving original filenames and MIME types.
- **Text-to-Video Steganography**: LSB modulation across sequential video frames in RGB color space.
- **File-to-Video Steganography**: Embeds binary files across frames and reassembles with lossless video encoding.
- **Lossless Video Pipeline**: Utilizes FFmpeg with `libx264rgb -crf 0` to prevent lossy Discrete Cosine Transform (DCT) quantization from destroying LSBs.
- **Audio Stream Multiplexing**: Automatically extracts and preserves the carrier video's original soundtrack.
- **AES-256-GCM Authenticated Encryption**: Optional password protection using PBKDF2-HMAC-SHA256 (100,000 iterations), random 16-byte salt, 12-byte nonce, and 128-bit authentication tag.
- **Self-Describing Binary Envelope**: 18-byte structured header with magic signature (`STEG`), versioning, format flags, and CRC32 integrity verification.
- **Live Session Telemetry**: Real session metrics tracking total processed files, audio operations, video operations, and a real-time operation log.
- **Interactive Cyberpunk UI**: Built with React, Tailwind CSS, Lucide icons, audio & video preview players, real-time capacity meters, and drag-and-drop file uploaders.

---

## 2. Project Architecture

```
Steganography/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_audio.py     # Audio embed, extract, capacity, and download endpoints
│   │   │   ├── routes_video.py     # Video embed, extract, capacity, and download endpoints
│   │   │   ├── routes_stats.py     # Session telemetry endpoints
│   │   │   └── routes_health.py    # System diagnostics and FFmpeg health check
│   │   ├── core/
│   │   │   ├── config.py           # Configuration and FFmpeg auto-detection
│   │   │   ├── payload.py          # Binary envelope serialization, CRC32, and parsing
│   │   │   └── security.py         # AES-256-GCM encryption and PBKDF2 key derivation
│   │   ├── services/
│   │   │   ├── audio_stego.py      # Audio PCM WAV LSB engine
│   │   │   ├── video_stego.py      # Video frame LSB engine and FFmpeg pipeline
│   │   │   └── stats_service.py    # In-memory session tracking service
│   │   └── main.py                 # FastAPI application root & CORS
│   ├── tests/
│   │   ├── test_security.py        # Cryptography unit tests
│   │   ├── test_payload.py         # Envelope & CRC32 tests
│   │   ├── test_audio_stego.py     # Audio embedding & recovery tests
│   │   ├── test_video_stego.py     # Video embedding & recovery tests
│   │   └── test_api.py             # HTTP API end-to-end route tests
│   ├── temp_uploads/               # Isolated temporary media storage
│   ├── requirements.txt            # Python dependencies
│   ├── run_backend.py              # Backend runner script
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/             # Sidebar, Header, FileDropzone, CapacityMeter, Toast
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # Overview, live session stats, recent operations
│   │   │   ├── AudioStego.jsx      # Audio embedding workflow & audio preview player
│   │   │   ├── VideoStego.jsx      # Video embedding workflow & video preview player
│   │   │   ├── ExtractData.jsx     # Universal audio/video payload extractor
│   │   │   ├── HowItWorks.jsx      # In-depth educational guide to LSB and codecs
│   │   │   └── AboutProject.jsx    # System specifications and live diagnostics
│   │   ├── api.js                  # Axios client for REST API communication
│   │   ├── App.jsx                 # Main application state and page switcher
│   │   └── index.css               # Cyberpunk styling & theme configuration
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
├── sample_media/                   # Pre-generated non-sensitive test media
│   ├── sample_audio.wav            # 3-second 44.1kHz stereo WAV
│   ├── sample_video.mp4            # 2-second 320x240 MP4
│   ├── secret_intel.txt            # Sample secret message
│   └── secret_document.pdf         # Sample binary PDF
├── start_backend.bat / .ps1        # 1-click backend startup script
├── start_frontend.bat / .ps1       # 1-click frontend startup script
└── create_sample_media.py          # Script to generate sample media
```

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React, Axios
- **Backend**: Python 3.12, FastAPI, Uvicorn, NumPy, SciPy, SoundFile, OpenCV Headless, Pillow, Cryptography (AES-GCM), Pytest, HTTPX
- **Media Engine**: FFmpeg (Essentials build) with `libx264rgb` and `ffv1` lossless profiles

---

## 4. Installation and Setup

### Prerequisites
1. **Python 3.10+**: Ensure Python is installed.
2. **Node.js LTS (v20+)**: Ensure Node.js and npm are installed.
3. **FFmpeg**: Required for video frame reassembly and audio preservation.
   - On Windows via Winget: `winget install --id Gyan.FFmpeg.Essentials`
   - Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to `PATH`.

### Step 1: Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Frontend Setup
```powershell
# Navigate to frontend directory
cd ../frontend

# Install node dependencies
npm install
```

---

## 5. Running the Application

### Option A: Using Startup Scripts (Windows)
Double-click or execute in separate terminals:
- `start_backend.bat` (or `.\start_backend.ps1`)
- `start_frontend.bat` (or `.\start_frontend.ps1`)

### Option B: Manual Command Line Execution

**Start the Backend:**
```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI server will start at `http://127.0.0.1:8000` with interactive API docs at `http://127.0.0.1:8000/docs`.

**Start the Frontend:**
```powershell
cd frontend
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 6. How to Test with Sample Media

Pre-generated media is available in `sample_media/`:

1. **Audio Steganography Workflow:**
   - Open the web application and navigate to **Audio Steganography**.
   - Drag and drop `sample_media/sample_audio.wav`.
   - Enter secret text or upload `sample_media/secret_document.pdf`.
   - (Optional) Toggle **AES-256-GCM Encryption** and enter a password (e.g. `CyberSecret123`).
   - Click **Embed Secret Data into Audio**.
   - Play the generated stego audio directly in the browser player, verify acoustic fidelity, and click **Download Stego WAV**.

2. **Hidden Data Extraction Workflow:**
   - Navigate to **Extract Hidden Data**.
   - Upload the newly downloaded stego audio file.
   - Enter the password if encryption was applied.
   - Click **Extract Hidden Data**.
   - View the recovered text or download the exact reconstructed binary PDF.

3. **Video Steganography Workflow:**
   - Navigate to **Video Steganography**.
   - Upload `sample_media/sample_video.mp4`.
   - Choose text or file payload, set password, and click **Embed Secret Data into Video**.
   - Watch the video play in the preview player with sound preserved, and extract it via **Extract Hidden Data**.

---

## 7. Running the Automated Test Suite

A test suite containing 20 tests validates cryptography, binary envelope integrity, audio LSB embedding, video lossless reassembly, and full REST API routes:

```powershell
$env:PYTHONPATH = "backend"
backend\venv\Scripts\pytest backend\tests -v
```

All 20 tests verify:
- Correct password decryption & wrong password rejection.
- Tampered ciphertext rejection (authenticated GCM tag verification).
- Text & arbitrary file byte-for-byte exact recovery.
- CRC32 checksum mismatch detection upon carrier truncation or corruption.
- Audio and video capacity bounds and insufficient capacity exceptions.
- API endpoints (`/api/health`, `/api/stats`, `/api/audio/embed`, `/api/audio/extract`, etc.).

---

## 8. Technical Disclosures & Steganography Limitations

- **Carrier Lossless Requirement**: LSB steganography modifies the lowest energy bits of raw samples. If the resulting stego WAV file is converted to a lossy format (e.g. MP3, AAC, OGG) or uploaded to social media platforms that re-encode audio/video, lossy psychoacoustic compression or DCT quantization will discard the LSBs.
- **Video Codecs**: Standard H.264/H.265 lossy compression alters pixel values during quantization. This application explicitly uses lossless H.264 (`-c:v libx264rgb -crf 0`) and `ffv1` to guarantee 100% bit preservation across video frames.
- **Local Execution**: All media operations and cryptographic operations are executed locally on the backend. No user data is sent to external cloud APIs.


---

## 9. 📱 Real SMS Configuration (Optional)

StegoCyber supports **real SMS delivery** for OTP (One-Time Password) verification when extracting files with recipient verification enabled. This feature is **optional** but provides enhanced security with multi-factor authentication.

### SMS Providers Supported

1. **Twilio** (Global) - ⭐ **Recommended**
   - **Free Trial:** $15 credit (~2000 SMS)
   - **Cost:** $0.0075-$0.20 per SMS
   - **Setup:** 2 minutes
   - **Best For:** Production, worldwide delivery

2. **Fast2SMS** (India only)
   - **Cost:** ₹0.15 per SMS (~$0.002)
   - **Setup:** 3 minutes
   - **Best For:** Budget India deployments

3. **2Factor.in** (India only)
4. **TextBee** (Free - uses your Android phone SIM)
5. **Custom Webhook** (for advanced integrations)

### Quick Setup (Twilio - Recommended)

1. **Sign up for Twilio (Free):**
   ```
   Visit: https://www.twilio.com/try-twilio
   Get $15 free credit (no credit card required)
   ```

2. **Get Credentials:**
   - Go to [Twilio Console](https://console.twilio.com)
   - Copy your Account SID and Auth Token
   - Get a trial phone number (click the big button)

3. **Configure StegoCyber:**
   
   **Option A: Via Web UI (Easiest)**
   - Start the application
   - Click "SMS Configuration" in the sidebar
   - Paste your Twilio credentials and save

   **Option B: Via .env File**
   ```env
   # Edit backend/.env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_FROM_NUMBER=+15551234567
   ```

4. **Test It:**
   ```powershell
   cd backend
   python test_sms.py
   # Enter your phone number and check for SMS!
   ```

### Verification

Check if SMS is configured:
```powershell
python check_sms_setup.py
```

This will show which SMS providers are active and guide you through setup if needed.

### Important Notes

- **Without SMS configured:** OTP codes appear in the browser (dev mode)
- **With SMS configured:** Real text messages sent to phone numbers
- **Twilio trial:** Can only send to verified phone numbers (verify in Twilio Console)
- **Upgrade to paid:** No monthly fee, pay-as-you-go, removes trial restrictions

### Documentation

- **Quick Start (5 min):** See `QUICKSTART_SMS.md`
- **Full Setup Guide:** See `SMS_SETUP_GUIDE.md`
- **Complete Reference:** See `SMS_README.md`

### Troubleshooting

**"No SMS gateway configured"**
- Run `python check_sms_setup.py` to verify setup
- Ensure `backend/.env` has SMS credentials
- Restart the backend after configuration changes

**"The number is unverified" (Twilio trial)**
- Add phone numbers to verified list in Twilio Console
- Or upgrade to paid account (no monthly fee)

---

## 10. Additional Resources

- **SMS Test Script:** `backend/test_sms.py` - Send a test SMS to your phone
- **Setup Checker:** `check_sms_setup.py` - Verify your SMS configuration
- **Sample Media Generator:** `create_sample_media.py` - Generate test files

---

## 11. License & Educational Purpose

This project is designed for **cybersecurity education and research**. It demonstrates:
- LSB steganography techniques and their detection challenges
- Authenticated encryption (AES-256-GCM) and its role in securing embedded payloads
- Multi-factor authentication with SMS OTP and biometric face verification
- Full-stack secure application development best practices

**Disclaimer:** Use responsibly and in compliance with applicable laws and regulations.
