import React, { useRef, useState, useEffect, useCallback } from 'react';
import { 
  Camera, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  ShieldAlert, 
  ShieldCheck, 
  X, 
  Eye, 
  Smile, 
  User, 
  Sparkles,
  AlertTriangle 
} from 'lucide-react';
import { detectFace } from '../api';

export default function BiometricScanner({ onCapture, onCancel, capturedImage, setCapturedImage }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const trackingIntervalRef = useRef(null);
  const isCheckingRef = useRef(false);

  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [flash, setFlash] = useState(false);

  // Real-time Face & Feature Status
  const [trackingStatus, setTrackingStatus] = useState('INITIALIZING'); // 'INITIALIZING' | 'NO_FACE' | 'MASK_DETECTED' | 'LANDMARKS_MISSING' | 'FACE_VALID' | 'FACE_TOO_SMALL'
  const [trackingMessage, setTrackingMessage] = useState('Initializing Face AI Sensor...');
  const [faceBbox, setFaceBbox] = useState(null);
  const [isFaceReady, setIsFaceReady] = useState(false);

  // Live checklist of required facial landmarks
  const [features, setFeatures] = useState({
    personPresent: false,
    eyesVisible: false,
    noseVisible: false,
    mouthVisible: false,
    unmasked: false,
    centered: false
  });

  const startCamera = async () => {
    setCameraError(null);
    setTrackingStatus('INITIALIZING');
    setTrackingMessage('Connecting camera sensor...');
    setIsFaceReady(false);
    setFeatures({
      personPresent: false,
      eyesVisible: false,
      noseVisible: false,
      mouthVisible: false,
      unmasked: false,
      centered: false
    });

    try {
      // Check API support (Safari 11+ and all modern browsers)
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera API not supported. Please use Chrome, Firefox, or Safari 11+.");
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });

      streamRef.current = stream;
      if (videoRef.current) {
        const video = videoRef.current;
        video.srcObject = stream;

        const handleReady = () => {
          const playPromise = video.play();
          if (playPromise !== undefined) {
            playPromise
              .then(() => {
                setCameraActive(true);
                setTrackingStatus('NO_FACE');
                setTrackingMessage('Position your face clearly in the camera frame.');
              })
              .catch((e) => {
                console.warn("Autoplay blocked:", e);
                setCameraActive(true);
                setTrackingStatus('NO_FACE');
                setTrackingMessage('Tap camera area to activate, then position your face.');
              });
          } else {
            setCameraActive(true);
          }
        };

        video.onloadedmetadata = handleReady;
        video.oncanplay = () => {
          if (!cameraActive) handleReady();
        };
      }
    } catch (err) {
      console.warn("Webcam access error:", err);
      // Provide Mac-specific helpful error messages
      let msg = err.message || "Camera access denied.";
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = "Camera access denied. On Mac: go to System Settings → Privacy & Security → Camera → enable access for your browser.";
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = "No camera found. Please connect a camera and try again.";
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = "Camera is in use by another app. Close other apps using the camera and try again.";
      } else if (err.name === 'OverconstrainedError') {
        msg = "Camera does not meet requirements. Try a different camera.";
      }
      setCameraError(msg);
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (trackingIntervalRef.current) {
      clearInterval(trackingIntervalRef.current);
      trackingIntervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  // Real-time frame analysis
  const checkCurrentFrame = useCallback(async () => {
    const video = videoRef.current;
    if (
      !video || 
      !cameraActive || 
      isCheckingRef.current || 
      video.readyState < 2 || 
      !video.videoWidth || 
      !video.videoHeight
    ) {
      return;
    }

    try {
      isCheckingRef.current = true;
      const vw = video.videoWidth;
      const vh = video.videoHeight;

      // Downsample frame for fast, low-latency tracking
      const canvas = document.createElement('canvas');
      canvas.width = 360;
      canvas.height = Math.round(360 * (vh / vw));
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const frameB64 = canvas.toDataURL('image/jpeg', 0.70);
      const res = await detectFace(frameB64);

      const feat = res.features || {};
      const newFeatures = {
        personPresent: Boolean(res.has_face),
        eyesVisible: Boolean(feat.eyes_visible),
        noseVisible: Boolean(feat.nose_visible),
        mouthVisible: Boolean(feat.mouth_visible),
        unmasked: Boolean(res.is_unmasked),
        centered: Boolean(feat.centered)
      };
      setFeatures(newFeatures);

      // STRICT CHECK: Person must be present, with eyes, nose, mouth visible and without mask!
      if (!res.has_face) {
        setTrackingStatus('NO_FACE');
        setTrackingMessage('No person detected. Please position your face in the camera.');
        setFaceBbox(null);
        setIsFaceReady(false); // IMMEDIATE rejection, zero persistence
      } else if (!res.is_valid || res.status === 'LANDMARKS_MISSING') {
        setTrackingStatus('LANDMARKS_MISSING');
        setTrackingMessage(res.message || 'Face features not clear. Look directly at camera.');
        setFaceBbox(res.bbox);
        setIsFaceReady(false); // IMMEDIATE rejection
      } else if (!res.is_unmasked || res.status === 'MASK_DETECTED') {
        setTrackingStatus('MASK_DETECTED');
        setTrackingMessage(res.message || 'Mask detected! Please remove face covering.');
        setFaceBbox(res.bbox);
        setIsFaceReady(false); // IMMEDIATE rejection
      } else if (res.status === 'FACE_TOO_SMALL') {
        setTrackingStatus('FACE_TOO_SMALL');
        setTrackingMessage('Move closer to the camera so your face is clear.');
        setFaceBbox(res.bbox);
        setIsFaceReady(false); // IMMEDIATE rejection
      } else if (res.is_valid && res.has_face && res.is_unmasked) {
        setTrackingStatus('FACE_VALID');
        setTrackingMessage('Full face verified: 2 eyes, nose, lips clearly visible.');
        setFaceBbox(res.bbox);
        setIsFaceReady(true);
      } else {
        setIsFaceReady(false);
      }
    } catch (err) {
      console.debug("Tracking cycle exception:", err);
    } finally {
      isCheckingRef.current = false;
    }
  }, [cameraActive]);

  useEffect(() => {
    if (cameraActive && !capturedImage) {
      trackingIntervalRef.current = setInterval(checkCurrentFrame, 350);
    } else {
      if (trackingIntervalRef.current) {
        clearInterval(trackingIntervalRef.current);
        trackingIntervalRef.current = null;
      }
    }
    return () => {
      if (trackingIntervalRef.current) {
        clearInterval(trackingIntervalRef.current);
      }
    };
  }, [cameraActive, capturedImage, checkCurrentFrame]);

  useEffect(() => {
    if (!capturedImage) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [capturedImage]);

  // Capture Photo with strict server-side validation
  const handleCapturePhoto = async () => {
    const video = videoRef.current;
    if (!video || !cameraActive || !isFaceReady || !video.videoWidth || !video.videoHeight) return;

    setIsScanning(true);
    setFlash(true);

    try {
      const width = video.videoWidth || 640;
      const height = video.videoHeight || 480;

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) throw new Error("Could not create canvas context.");
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const base64Jpg = canvas.toDataURL('image/jpeg', 0.90);

      // Verify the high-resolution captured snapshot strictly
      const verifyRes = await detectFace(base64Jpg);

      if (!verifyRes.has_face) {
        setFlash(false);
        setIsScanning(false);
        setIsFaceReady(false);
        setTrackingStatus('NO_FACE');
        alert('Photo Blocked: No person detected in the frame. You must be visible in front of the camera.');
        return;
      }

      if (!verifyRes.is_valid || !verifyRes.is_unmasked) {
        setFlash(false);
        setIsScanning(false);
        setIsFaceReady(false);
        alert(`Photo Blocked: ${verifyRes.message || 'Full face with visible eyes, nose, and lips without mask is required.'}`);
        return;
      }

      // Valid full unmasked face verified!
      setTimeout(() => {
        setFlash(false);
        setIsScanning(false);
        stopCamera();
        setCapturedImage(base64Jpg);
        if (onCapture) onCapture(base64Jpg);
      }, 150);
    } catch (err) {
      console.error("Frame capture failed:", err);
      setIsScanning(false);
      setFlash(false);
      setCameraError("Failed to snap picture from camera.");
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setIsFaceReady(false);
    startCamera();
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-950/90 border border-cyan-500/40 shadow-glow-cyan space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400">
            <Camera className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">Live Biometric Face Scanner</h4>
            <p className="text-[11px] text-slate-400">Requires person visible: 2 eyes, nose, lips without mask</p>
          </div>
        </div>

        {onCancel && (
          <button onClick={onCancel} className="text-slate-500 hover:text-slate-300">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Camera Viewport / Captured Preview */}
      <div 
        onClick={() => {
          if (videoRef.current && videoRef.current.paused) {
            videoRef.current.play().then(() => setCameraActive(true)).catch(() => {});
          }
        }}
        className="relative w-full aspect-video rounded-xl overflow-hidden bg-black border border-slate-800 flex items-center justify-center cursor-pointer"
      >
        {flash && (
          <div className="absolute inset-0 bg-white z-30 transition-opacity duration-150" />
        )}

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          // @ts-ignore
          webkit-playsinline="true"
          className={`w-full h-full object-cover transform -scale-x-100 transition-opacity duration-300 ${
            capturedImage ? 'hidden' : 'block'
          } ${cameraActive ? 'opacity-100' : 'opacity-0'}`}
        />

        {/* Captured Image Display */}
        {capturedImage && (
          <div className="relative w-full h-full animate-fade-in">
            <img
              src={capturedImage}
              alt="Captured Biometric Face"
              className="w-full h-full object-cover"
            />
            <div className="absolute top-3 left-3 bg-emerald-950/90 border border-emerald-500/80 px-3 py-1.5 rounded-lg text-xs font-mono text-emerald-300 flex items-center gap-2 backdrop-blur-md shadow-lg">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Face Verified (Eyes, Nose, Lips Confirmed) • Logged to Audit Vault</span>
            </div>
          </div>
        )}

        {/* Live HUD Reticle & Indicators */}
        {!capturedImage && cameraActive && (
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div
              className={`w-60 h-60 border-2 relative rounded-2xl transition-all duration-200 ${
                isFaceReady
                  ? 'border-emerald-400 shadow-[0_0_30px_rgba(52,211,153,0.6)]'
                  : trackingStatus === 'MASK_DETECTED'
                  ? 'border-amber-400 shadow-[0_0_25px_rgba(251,191,36,0.5)]'
                  : 'border-rose-500/70 shadow-[0_0_20px_rgba(244,63,94,0.35)]'
              }`}
            >
              {/* Reticle Corners */}
              <div className={`absolute -top-1 -left-1 w-5 h-5 border-t-2 border-l-2 ${isFaceReady ? 'border-emerald-400' : 'border-rose-500'}`} />
              <div className={`absolute -top-1 -right-1 w-5 h-5 border-t-2 border-r-2 ${isFaceReady ? 'border-emerald-400' : 'border-rose-500'}`} />
              <div className={`absolute -bottom-1 -left-1 w-5 h-5 border-b-2 border-l-2 ${isFaceReady ? 'border-emerald-400' : 'border-rose-500'}`} />
              <div className={`absolute -bottom-1 -right-1 w-5 h-5 border-b-2 border-r-2 ${isFaceReady ? 'border-emerald-400' : 'border-rose-500'}`} />

              {/* Scan laser */}
              <div className="absolute inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-glow-cyan animate-bounce" />
            </div>

            {/* Live Status Pill Overlay */}
            <div className="absolute bottom-3 inset-x-0 flex flex-col items-center gap-1 text-center px-4">
              <span
                className={`text-[11px] font-mono px-3.5 py-1 rounded-full border backdrop-blur-md flex items-center gap-1.5 shadow-md ${
                  isFaceReady
                    ? 'bg-emerald-950/90 border-emerald-500 text-emerald-300 font-bold'
                    : trackingStatus === 'MASK_DETECTED'
                    ? 'bg-amber-950/90 border-amber-500 text-amber-300 font-bold'
                    : 'bg-rose-950/90 border-rose-500 text-rose-300 font-bold'
                }`}
              >
                {isFaceReady && <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
                {!isFaceReady && trackingStatus === 'MASK_DETECTED' && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                {!isFaceReady && trackingStatus !== 'MASK_DETECTED' && <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />}
                <span>
                  {isFaceReady && 'PERSON & FULL FACE VERIFIED • READY TO CAPTURE'}
                  {!isFaceReady && trackingStatus === 'MASK_DETECTED' && 'MASK / OCCLUSION DETECTED • REMOVE MASK'}
                  {!isFaceReady && trackingStatus === 'NO_FACE' && 'NO PERSON DETECTED • STEP INTO FRAME'}
                  {!isFaceReady && trackingStatus === 'LANDMARKS_MISSING' && 'LOOK DIRECTLY AT CAMERA (EYES & LIPS REQUIRED)'}
                  {!isFaceReady && trackingStatus === 'FACE_TOO_SMALL' && 'MOVE CLOSER TO CAMERA'}
                  {!isFaceReady && trackingStatus === 'INITIALIZING' && 'CONNECTING SENSOR...'}
                </span>
              </span>

              <span className="text-[10px] text-slate-300 font-mono bg-black/70 px-2 py-0.5 rounded">
                {trackingMessage}
              </span>
            </div>
          </div>
        )}

        {/* Fallback when camera not active */}
        {!capturedImage && !cameraActive && (
          <div className="p-6 text-center space-y-3 z-10">
            <ShieldAlert className="w-8 h-8 mx-auto text-amber-400" />
            <p className="text-xs text-slate-300 max-w-sm">
              {cameraError || "Camera starting up... Please allow camera permissions."}
            </p>
            <div className="flex justify-center pt-2">
              <button
                type="button"
                onClick={startCamera}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-cyan-300 bg-cyan-950 border border-cyan-800 hover:bg-cyan-900 transition-colors flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Camera
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Live Biometric Feature Verification Checklist */}
      {!capturedImage && cameraActive && (
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono space-y-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-1.5 font-bold uppercase tracking-wider">
            <span>Biometric Feature Checklist</span>
            <span className={isFaceReady ? 'text-emerald-400' : 'text-amber-400'}>
              {isFaceReady ? 'All Criteria Met ✓' : 'Requirements Incomplete ✗'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-0.5 text-[11px]">
            {/* Person Present */}
            <div className={`p-2 rounded-lg border flex items-center gap-2 ${
              features.personPresent ? 'bg-emerald-950/30 border-emerald-700/60 text-emerald-300' : 'bg-slate-950 border-slate-800 text-slate-500'
            }`}>
              {features.personPresent ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
              <span>Person Visible</span>
            </div>

            {/* Both Eyes */}
            <div className={`p-2 rounded-lg border flex items-center gap-2 ${
              features.eyesVisible ? 'bg-emerald-950/30 border-emerald-700/60 text-emerald-300' : 'bg-slate-950 border-slate-800 text-slate-500'
            }`}>
              {features.eyesVisible ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
              <span>2 Eyes Visible</span>
            </div>

            {/* Nose & Lips */}
            <div className={`p-2 rounded-lg border flex items-center gap-2 ${
              features.noseVisible && features.mouthVisible ? 'bg-emerald-950/30 border-emerald-700/60 text-emerald-300' : 'bg-slate-950 border-slate-800 text-slate-500'
            }`}>
              {features.noseVisible && features.mouthVisible ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
              <span>Nose & Lips</span>
            </div>

            {/* Unmasked */}
            <div className={`p-2 rounded-lg border flex items-center gap-2 ${
              features.unmasked && features.personPresent ? 'bg-emerald-950/30 border-emerald-700/60 text-emerald-300' : 'bg-slate-950 border-slate-800 text-slate-500'
            }`}>
              {features.unmasked && features.personPresent ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
              <span>Without Mask</span>
            </div>
          </div>
        </div>
      )}

      {/* Action Controls */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pt-1">
        {capturedImage ? (
          <button
            type="button"
            onClick={handleRetake}
            className="w-full py-3 rounded-xl text-xs font-semibold text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retake Face Scan</span>
          </button>
        ) : (
          <>
            <button
              type="button"
              disabled={!cameraActive || isScanning || !isFaceReady}
              onClick={handleCapturePhoto}
              className={`flex-1 py-3.5 px-4 rounded-xl text-xs font-bold uppercase tracking-wider text-white transition-all flex items-center justify-center gap-2 shrink-0 ${
                isFaceReady
                  ? 'bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 shadow-[0_0_20px_rgba(16,185,129,0.5)] cursor-pointer'
                  : 'bg-slate-800/80 border border-slate-700/60 opacity-50 cursor-not-allowed text-slate-400'
              }`}
            >
              {isScanning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Verifying Frame...</span>
                </>
              ) : (
                <>
                  <Camera className="w-4 h-4" />
                  <span>
                    {isFaceReady
                      ? 'Capture Live Face Scan'
                      : trackingStatus === 'MASK_DETECTED'
                      ? 'Blocked: Remove Mask'
                      : trackingStatus === 'NO_FACE'
                      ? 'Blocked: Person Not In Frame'
                      : 'Blocked: Face Incomplete'}
                  </span>
                </>
              )}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
