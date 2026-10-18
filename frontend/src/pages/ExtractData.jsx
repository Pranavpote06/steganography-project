import React, { useState } from 'react';
import {
  SearchCode,
  Lock,
  Unlock,
  Copy,
  Download,
  CheckCircle2,
  FileArchive,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Music,
  Video,
  Camera,
  KeyRound,
  UserCheck,
} from 'lucide-react';
import FileDropzone from '../components/FileDropzone';
import BiometricScanner from '../components/BiometricScanner';
import {
  extractAudio,
  extractVideo,
  inspectCarrier,
  verifyAndExtract,
} from '../api';

export default function ExtractData({ showToast, onOperationComplete }) {
  // Carrier state
  const [carrierFile, setCarrierFile] = useState(null);
  const [carrierInspection, setCarrierInspection] = useState(null);
  const [isInspecting, setIsInspecting] = useState(false);

  // Auth state
  const [password, setPassword] = useState('');

  // Face Scan state
  const [capturedFaceImage, setCapturedFaceImage] = useState(null);

  // Extraction & Result states
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedResult, setExtractedResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const isAudio = carrierFile?.name.toLowerCase().endsWith('.wav');
  const isVideo = carrierFile &&
    ['.mp4', '.avi', '.mov', '.mkv'].some(ext =>
      carrierFile.name.toLowerCase().endsWith(ext)
    );

  const needsFaceVerify = Boolean(carrierInspection?.has_recipient_verify);
  const needsPassword = Boolean(
    carrierInspection?.has_password || carrierInspection?.is_encrypted
  );

  const handleCarrierSelect = async (file) => {
    setCarrierFile(file);
    setExtractedResult(null);
    setErrorMsg(null);
    setCapturedFaceImage(null);
    setIsInspecting(true);

    try {
      const inspection = await inspectCarrier(file);
      setCarrierInspection(inspection);
      if (inspection.has_recipient_verify) {
        showToast({
          type: 'info',
          title: 'Biometric Lock Detected',
          message: 'This file requires a Decryption Password + Live Face Scan to unlock.',
        });
      } else if (inspection.has_stego) {
        showToast({
          type: 'success',
          title: 'Stego Carrier Detected',
          message: inspection.has_password
            ? 'Encrypted payload found. Enter the decryption password to extract.'
            : 'Unencrypted payload found. Click Extract to recover the hidden data.',
        });
      }
    } catch (err) {
      console.warn('Carrier inspection warning:', err);
      setCarrierInspection(null);
    } finally {
      setIsInspecting(false);
    }
  };

  const handleClearCarrier = () => {
    setCarrierFile(null);
    setCarrierInspection(null);
    setExtractedResult(null);
    setErrorMsg(null);
    setPassword('');
    setCapturedFaceImage(null);
  };

  const handleExtract = async (e) => {
    e.preventDefault();
    if (!carrierFile) {
      showToast({ type: 'warning', title: 'File Required', message: 'Please upload a carrier media file.' });
      return;
    }

    if (needsFaceVerify && !capturedFaceImage) {
      showToast({ type: 'warning', title: 'Face Scan Required', message: 'Please complete the live biometric face scan.' });
      return;
    }

    setIsExtracting(true);
    setErrorMsg(null);

    try {
      let result;

      if (needsFaceVerify) {
        // Biometric + Password extraction path
        result = await verifyAndExtract({
          carrierFile,
          faceImage: capturedFaceImage,
          password: password.trim() || null,
        });
      } else {
        // Standard extraction path (password or plain)
        if (isAudio) {
          result = await extractAudio({
            audioFile: carrierFile,
            password: password.trim() || null,
          });
        } else if (isVideo) {
          result = await extractVideo({
            videoFile: carrierFile,
            password: password.trim() || null,
          });
        } else {
          throw new Error('Unsupported carrier format. Upload a .wav audio or .mp4/.avi video.');
        }
      }

      setExtractedResult(result);
      showToast({
        type: 'success',
        title: 'Data Recovered & Verified',
        message: result.face_captured
          ? 'Biometric face scan captured & logged to sender! Payload unlocked.'
          : 'Payload recovered successfully.',
      });

      if (onOperationComplete) onOperationComplete();
    } catch (err) {
      const msg = err.response?.data?.detail || err.message;
      setErrorMsg(msg);
      showToast({ type: 'error', title: 'Unlock Failed', message: msg });
    } finally {
      setIsExtracting(false);
    }
  };

  const handleCopyText = () => {
    if (extractedResult?.text) {
      navigator.clipboard.writeText(extractedResult.text);
      showToast({ type: 'success', title: 'Copied to Clipboard', message: 'Recovered secret text copied.' });
    }
  };

  const handleDownloadFile = () => {
    if (!extractedResult?.data_base64) return;
    try {
      const byteCharacters = atob(extractedResult.data_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: extractedResult.mime_type || 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = extractedResult.filename || 'recovered_file.bin';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToast({ type: 'success', title: 'Download Started', message: `Downloading ${extractedResult.filename}` });
    } catch {
      showToast({ type: 'error', title: 'Download Error', message: 'Failed to reconstruct file from payload.' });
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const canSubmit =
    !!carrierFile &&
    !isExtracting &&
    (!needsFaceVerify || !!capturedFaceImage);

  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
            <SearchCode className="w-5 h-5" />
            <span className="text-xs font-mono font-semibold tracking-wider uppercase">Data Recovery Engine</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Extract Hidden Data</h2>
          <p className="text-sm text-slate-400 mt-1">
            Unlock steganographic audio (.wav) or video (.mp4/.avi) carriers using a decryption password and live face verification.
          </p>
        </div>

        {(carrierFile || extractedResult) && (
          <button
            onClick={handleClearCarrier}
            className="self-start sm:self-auto px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/60 transition-colors flex items-center gap-2"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Form</span>
          </button>
        )}
      </div>

      {/* Step 1: Upload Stego Media */}
      <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] border border-cyan-800/60">1</span>
            Upload Steganographic Media Carrier
          </span>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="flex items-center gap-1 font-mono">
              <Music className="w-3.5 h-3.5 text-cyan-400" /> WAV
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 font-mono">
              <Video className="w-3.5 h-3.5 text-purple-400" /> MP4 / AVI
            </span>
          </div>
        </div>

        <FileDropzone
          file={carrierFile}
          onFileSelect={handleCarrierSelect}
          onClear={handleClearCarrier}
          accept=".wav,.mp4,.avi,.mov,.mkv,audio/wav,video/*"
          title="Select Stego Media File"
          subtitle="Drag & drop stego audio or video file here"
          allowedExtensions={['.wav', '.mp4', '.avi', '.mov', '.mkv']}
        />

        {isInspecting && (
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-mono animate-pulse">
            <div className="w-3 h-3 border border-cyan-400/60 border-t-cyan-400 rounded-full animate-spin" />
            Scanning carrier signature...
          </div>
        )}

        {/* Carrier Inspection Result */}
        {carrierInspection && !isInspecting && (
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 animate-fade-in font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">CARRIER SIGNATURE:</span>
              <span className={carrierInspection.has_stego ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                {carrierInspection.has_stego ? 'STEGOCYBER HEADER DETECTED' : 'NO STEGANOGRAPHY FOUND'}
              </span>
            </div>

            {carrierInspection.has_stego && (
              <>
                <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
                  <span className="text-slate-400">ENCRYPTION:</span>
                  <span className={carrierInspection.is_encrypted || carrierInspection.has_password ? 'text-amber-300 font-bold' : 'text-slate-400'}>
                    {carrierInspection.is_encrypted || carrierInspection.has_password ? 'AES-256-GCM ENCRYPTED' : 'UNENCRYPTED'}
                  </span>
                </div>

                {carrierInspection.has_recipient_verify && (
                  <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
                    <span className="text-cyan-400 flex items-center gap-1.5">
                      <Camera className="w-3.5 h-3.5" />
                      BIOMETRIC LOCK:
                    </span>
                    <span className="text-purple-300 font-bold">PASSWORD + LIVE FACE SCAN REQUIRED</span>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Step 2: Decryption Password */}
        {carrierInspection?.has_stego && (
          <div className="space-y-4 pt-2 border-t border-slate-800/60 animate-fade-in">
            <div className="space-y-2">
              <label className="block text-xs font-mono uppercase tracking-wider flex items-center gap-2 text-slate-300">
                <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[11px] border border-slate-700">2</span>
                {needsFaceVerify ? 'Decryption Password (required for biometric unlock)' : 'Decryption Password'}
                {!needsPassword && !needsFaceVerify && (
                  <span className="ml-1 text-slate-500 normal-case font-normal">(leave empty if not encrypted)</span>
                )}
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={
                    needsFaceVerify
                      ? 'Enter the decryption password set by the sender...'
                      : 'Enter passphrase if encrypted with AES-256-GCM...'
                  }
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                />
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              </div>
            </div>

            {/* Step 3: Live Face Scanner (only when biometric lock detected) */}
            {needsFaceVerify && (
              <div className="space-y-3 animate-fade-in">
                <label className="block text-xs font-mono uppercase tracking-wider flex items-center justify-between text-cyan-300">
                  <span className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] border border-cyan-800/60">3</span>
                    Live Biometric Face Scan
                  </span>
                  <span className="text-[10px] text-slate-400 normal-case font-normal">Your face photo will be transmitted to the sender</span>
                </label>

                {/* Info banner */}
                <div className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-700/40 text-xs font-mono text-purple-200 flex items-start gap-2.5">
                  <Camera className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                  <span>
                    This carrier is <strong>biometrically locked</strong>. You must pass a live face scan (no mask, no occlusion) to unlock the payload.
                    Your photo will be logged in the sender's audit vault.
                  </span>
                </div>

                <BiometricScanner
                  capturedImage={capturedFaceImage}
                  setCapturedImage={setCapturedFaceImage}
                />
              </div>
            )}
          </div>
        )}

        {/* Submit Action */}
        <button
          onClick={handleExtract}
          disabled={!canSubmit || !carrierInspection?.has_stego}
          className="w-full py-4 rounded-2xl text-sm font-bold tracking-wider uppercase text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 shadow-glow-cyan transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isExtracting ? (
            <>
              <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              <span>Verifying & Extracting Payload...</span>
            </>
          ) : (
            <>
              {needsFaceVerify ? <ShieldCheck className="w-5 h-5" /> : <SearchCode className="w-5 h-5" />}
              <span>
                {needsFaceVerify
                  ? 'Verify Biometrics & Unlock File'
                  : 'Extract Hidden Data'}
              </span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-200 text-sm flex items-start gap-3 animate-fade-in">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-semibold text-rose-300">Extraction Unsuccessful</div>
            <p className="text-xs text-rose-300/80">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* Result Card */}
      {extractedResult && (
        <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0f172a] to-[#0a0f1d] border border-cyan-500/40 shadow-glow-cyan space-y-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Hidden Data Recovered</h3>
                <span className="text-xs text-emerald-400 font-mono">
                  {extractedResult.face_captured
                    ? '2FA Verified • Face Photo Transmitted to Sender'
                    : 'Decryption Verified'}
                </span>
              </div>
            </div>

            <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 text-cyan-300 border border-cyan-800/40">
              {extractedResult.is_file ? 'FILE PAYLOAD' : 'TEXT PAYLOAD'}
            </span>
          </div>

          {/* Biometric Audit Notice */}
          {extractedResult.face_captured && (
            <div className="p-3.5 rounded-xl bg-slate-950 border border-cyan-800/40 text-xs font-mono text-cyan-300 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>
                Biometric Security Intercept Logged (ID: {extractedResult.audit_id}). Sender has been notified.
              </span>
            </div>
          )}

          {/* Text Result */}
          {!extractedResult.is_file ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                <span>Recovered Text ({extractedResult.length} characters):</span>
                <button
                  onClick={handleCopyText}
                  className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Text</span>
                </button>
              </div>
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 max-h-80 overflow-y-auto">
                <pre className="text-sm font-mono text-slate-100 whitespace-pre-wrap break-words">
                  {extractedResult.text}
                </pre>
              </div>
            </div>
          ) : (
            /* File Result */
            <div className="p-5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-950/80 border border-purple-800/50 flex items-center justify-center text-purple-400 shrink-0">
                  <FileArchive className="w-6 h-6" />
                </div>
                <div className="overflow-hidden">
                  <div className="text-sm font-bold text-white truncate">{extractedResult.filename}</div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    MIME: {extractedResult.mime_type} • Size: {formatSize(extractedResult.file_size)}
                  </div>
                </div>
              </div>

              <button
                onClick={handleDownloadFile}
                className="w-full py-3.5 rounded-xl text-sm font-bold text-slate-900 bg-cyan-400 hover:bg-cyan-300 shadow-glow-cyan transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                <span>Download Recovered File ({extractedResult.filename})</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
