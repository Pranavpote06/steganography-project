import React, { useState } from 'react';
import { 
  Music, 
  FileText, 
  Upload, 
  Lock, 
  Unlock, 
  Play, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  RotateCcw,
  Sparkles,
  Shield,
  FileCheck,
  Phone,
  Camera,
  UserCheck
} from 'lucide-react';
import FileDropzone from '../components/FileDropzone';
import CapacityMeter from '../components/CapacityMeter';
import { getAudioCapacity, embedAudio } from '../api';

export default function AudioStego({ showToast, onOperationComplete }) {
  // Carrier State
  const [carrierFile, setCarrierFile] = useState(null);
  const [carrierInfo, setCarrierInfo] = useState(null);
  const [isAnalyzingCarrier, setIsAnalyzingCarrier] = useState(false);
  const [carrierAudioUrl, setCarrierAudioUrl] = useState(null);

  // Payload State
  const [payloadType, setPayloadType] = useState('text'); // 'text' | 'file'
  const [secretText, setSecretText] = useState('');
  const [secretFile, setSecretFile] = useState(null);

  // Security State
  const [securityMode, setSecurityMode] = useState('face_scan'); // 'face_scan' | 'password' | 'none'
  const [senderId, setSenderId] = useState('Sender-HQ');
  const [password, setPassword] = useState('');

  // Processing & Result State
  const [isEmbedding, setIsEmbedding] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [stegoResult, setStegoResult] = useState(null);

  // Calculate approximate payload size
  let payloadBytes = 0;
  if (payloadType === 'text') {
    payloadBytes = new Blob([secretText]).size;
  } else if (secretFile) {
    payloadBytes = secretFile.size;
  }
  const isEncrypted = securityMode !== 'none';
  const estimatedEnvelopeBytes = payloadBytes > 0 
    ? payloadBytes + 50 + (isEncrypted ? 64 : 0) + (secretFile ? secretFile.name.length : 0)
    : 0;

  // Handle Carrier File Selection
  const handleCarrierSelect = async (file) => {
    const nameLower = file.name.toLowerCase();
    if (!nameLower.endsWith('.wav') && !nameLower.endsWith('.mp3')) {
      showToast({
        type: 'error',
        title: 'Unsupported Format',
        message: 'Please provide a WAV or MP3 audio file.'
      });
      return;
    }

    setCarrierFile(file);
    setCarrierAudioUrl(URL.createObjectURL(file));
    setStegoResult(null);
    setIsAnalyzingCarrier(true);

    if (nameLower.endsWith('.mp3')) {
      showToast({
        type: 'info',
        title: 'MP3 Detected',
        message: 'MP3 will be losslessly converted to WAV before embedding. Output stego file will be WAV.'
      });
    }

    try {
      const info = await getAudioCapacity(file);
      setCarrierInfo(info);
      showToast({
        type: 'info',
        title: 'Audio Carrier Analyzed',
        message: `Capacity: ${(info.capacity_bytes / 1024).toFixed(2)} KB (${info.duration_seconds}s, ${info.sample_rate}Hz)`
      });
    } catch (err) {
      showToast({
        type: 'error',
        title: 'Analysis Error',
        message: err.response?.data?.detail || err.message
      });
      setCarrierFile(null);
      setCarrierInfo(null);
    } finally {
      setIsAnalyzingCarrier(false);
    }
  };

  const handleClearCarrier = () => {
    setCarrierFile(null);
    setCarrierInfo(null);
    setCarrierAudioUrl(null);
    setStegoResult(null);
  };

  // Perform Embedding
  const handleEmbed = async (e) => {
    e.preventDefault();
    if (!carrierFile) {
      showToast({ type: 'warning', title: 'Carrier Required', message: 'Please select a carrier WAV or MP3 audio file.' });
      return;
    }
    if (payloadType === 'text' && !secretText.trim()) {
      showToast({ type: 'warning', title: 'Payload Required', message: 'Please enter the confidential text to hide.' });
      return;
    }
    if (payloadType === 'file' && !secretFile) {
      showToast({ type: 'warning', title: 'File Required', message: 'Please choose a secret file to hide.' });
      return;
    }
    if ((securityMode === 'face_scan' || securityMode === 'password') && !password.trim()) {
      showToast({ type: 'warning', title: 'Password Required', message: 'Please enter an encryption password.' });
      return;
    }

    try {
      setIsEmbedding(true);
      setUploadProgress(0);

      const result = await embedAudio({
        audioFile: carrierFile,
        payloadType,
        secretText,
        secretFile,
        password: (securityMode === 'face_scan' || securityMode === 'password') ? password.trim() : null,
        requireFaceScan: securityMode === 'face_scan',
        senderId: securityMode === 'face_scan' ? senderId.trim() : null,
        onProgress: (p) => setUploadProgress(p)
      });

      setStegoResult(result);
      showToast({
        type: 'success',
        title: 'Data Embedded Successfully',
        message: result.require_recipient_verify 
          ? `Stego WAV encoded with Recipient Phone 2FA & Face Scan Lock!`
          : `Stego WAV generated (${result.capacity_used_pct}% capacity utilized).`
      });

      if (onOperationComplete) onOperationComplete();
    } catch (err) {
      showToast({
        type: 'error',
        title: 'Embedding Failed',
        message: err.response?.data?.detail || err.message
      });
    } finally {
      setIsEmbedding(false);
    }
  };

  const handleResetAll = () => {
    if (window.confirm("Reset all audio embedding inputs and clear current result?")) {
      handleClearCarrier();
      setSecretText('');
      setSecretFile(null);
      setPassword('');
      setUsePassword(false);
      setStegoResult(null);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
            <Music className="w-5 h-5" />
            <span className="text-xs font-mono font-semibold tracking-wider uppercase">Audio Concealment Engine</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Audio Steganography</h2>
          <p className="text-sm text-slate-400 mt-1">
            Embed confidential messages or binary files into uncompressed PCM WAV waveforms using 1-bit LSB modulation.
          </p>
        </div>

        {(carrierFile || stegoResult) && (
          <button
            onClick={handleResetAll}
            className="self-start sm:self-auto px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/60 transition-colors flex items-center gap-2"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Operation</span>
          </button>
        )}
      </div>

      {/* Main Workflow Form */}
      <div className="space-y-6">
          {/* Step 1: Upload Carrier WAV */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] border border-cyan-800/60">
                  1
                </span>
                Carrier Audio File
              </span>
              <span className="text-[11px] text-slate-400">Supports: PCM .WAV · .MP3</span>
            </div>

            <FileDropzone
              file={carrierFile}
              onFileSelect={handleCarrierSelect}
              onClear={handleClearCarrier}
              accept=".wav,.mp3,audio/wav,audio/mpeg"
              title="Select Carrier Audio (WAV or MP3)"
              subtitle="Drag & drop WAV or MP3 file — MP3 is auto-converted to WAV before embedding"
              allowedExtensions={['.wav', '.mp3']}
            />

            {/* Carrier Audio Preview Player */}
            {carrierAudioUrl && (
              <div className="pt-2 space-y-2">
                <span className="text-[11px] text-slate-400 font-mono block">Original Audio Preview:</span>
                <audio controls src={carrierAudioUrl} className="w-full h-10 rounded-lg bg-slate-950" />
              </div>
            )}

            {/* Carrier Capacity Details */}
            {carrierInfo && (
              <CapacityMeter
                capacityBytes={carrierInfo.capacity_bytes}
                payloadBytes={estimatedEnvelopeBytes}
                details={carrierInfo}
              />
            )}
          </div>

          {/* Step 2: Secret Payload Configuration */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-purple-400 font-semibold uppercase tracking-wider flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-purple-950 flex items-center justify-center text-[11px] border border-purple-800/60">
                  2
                </span>
                Confidential Payload
              </span>

              {/* Mode Switcher */}
              <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800">
                <button
                  type="button"
                  onClick={() => setPayloadType('text')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    payloadType === 'text'
                      ? 'bg-purple-600 text-white shadow-glow-purple'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Secret Text
                </button>
                <button
                  type="button"
                  onClick={() => setPayloadType('file')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    payloadType === 'file'
                      ? 'bg-purple-600 text-white shadow-glow-purple'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Secret File
                </button>
              </div>
            </div>

            {payloadType === 'text' ? (
              <div className="space-y-2">
                <textarea
                  rows={5}
                  value={secretText}
                  onChange={(e) => setSecretText(e.target.value)}
                  placeholder="Type or paste confidential message to conceal inside the audio waveform..."
                  className="w-full p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 font-mono transition-colors"
                />
                <div className="flex justify-between text-[11px] font-mono text-slate-500">
                  <span>Characters: {secretText.length}</span>
                  <span>Estimated Size: {payloadBytes} bytes</span>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <FileDropzone
                  file={secretFile}
                  onFileSelect={(f) => setSecretFile(f)}
                  onClear={() => setSecretFile(null)}
                  title="Upload Secret Document or File"
                  subtitle="Any file type: PDF, DOCX, TXT, PNG, JPG, ZIP, etc."
                  allowedExtensions={['.txt', '.pdf', '.docx', '.png', '.jpg', '.zip']}
                />
                <p className="text-[11px] text-slate-400">
                  Binary exactness is strictly preserved. Original filename and MIME format will be restored upon extraction.
                </p>
              </div>
            )}
          </div>

          {/* Step 3: Access Security & Recipient Verification */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800/40 text-emerald-400">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">Access Protection & Biometrics</h4>
                  <p className="text-xs text-slate-400">AES-256-GCM Password & Live Webcam Face Scan Verification</p>
                </div>
              </div>

              {/* Security Selector */}
              <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800 text-[11px] font-mono">
                <button
                  type="button"
                  onClick={() => setSecurityMode('face_scan')}
                  className={`px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 ${
                    securityMode === 'face_scan'
                      ? 'bg-cyan-600 text-white shadow-glow-cyan'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Camera className="w-3 h-3" />
                  <span>Password + Face Scan</span>
                </button>
                <button
                  type="button"
                  onClick={() => setSecurityMode('password')}
                  className={`px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 ${
                    securityMode === 'password'
                      ? 'bg-purple-600 text-white shadow-glow-purple'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Lock className="w-3 h-3" />
                  <span>Password Only</span>
                </button>
                <button
                  type="button"
                  onClick={() => setSecurityMode('none')}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    securityMode === 'none'
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Plain
                </button>
              </div>
            </div>

            {/* Password + Face Scan Mode */}
            {securityMode === 'face_scan' && (
              <div className="space-y-3 pt-2 animate-fade-in">
                <div className="space-y-1">
                  <label className="block text-[11px] font-mono text-cyan-300 uppercase tracking-wider">
                    Decryption Password (AES-256-GCM)
                  </label>
                  <div className="relative">
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter confidential encryption passphrase..."
                      className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                    />
                    <Lock className="w-4 h-4 text-cyan-400 absolute left-3.5 top-3.5" />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    Sender Identifier (For Audit Log)
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={senderId}
                      onChange={(e) => setSenderId(e.target.value)}
                      placeholder="e.g. Agent-HQ or sender@organization.com"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                    />
                    <UserCheck className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-xs text-cyan-300 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold">
                    <Camera className="w-3.5 h-3.5 text-cyan-400" />
                    Live Biometric Face Scanner Active
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    When the recipient opens this stego carrier, they must enter this password and pass an 
                    unmasked live webcam face scan. <strong>Their face photo will be captured and saved in your Security Intercepts vault.</strong>
                  </p>
                </div>
              </div>
            )}

            {/* Password Only Mode */}
            {securityMode === 'password' && (
              <div className="space-y-2 pt-2 animate-fade-in">
                <div className="relative">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter confidential encryption passphrase..."
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-mono transition-colors"
                  />
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                </div>
                <p className="text-[11px] text-purple-400/80 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                  AES-256-GCM authenticated encryption with PBKDF2 (100k iterations).
                </p>
              </div>
            )}
          </div>

          {/* Action Button */}
          <button
            onClick={handleEmbed}
            disabled={isEmbedding || !carrierFile || estimatedEnvelopeBytes === 0}
            className="w-full py-4 rounded-2xl text-sm font-bold tracking-wider uppercase text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 shadow-glow-cyan transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isEmbedding ? (
              <>
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                <span>Embedding Confidential Payload ({uploadProgress}%)...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Embed Secret Data into Audio</span>
              </>
            )}
          </button>
        </div>

      {/* Stego Result Card - Full Width Centered */}
      {stegoResult && (
        <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0f172a] to-[#0a0f1d] border border-cyan-500/40 shadow-glow-cyan space-y-6 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
              <FileCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Stego Audio Ready</h3>
              <span className="text-xs text-emerald-400 font-mono flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Payload Encoded & Verified
              </span>
            </div>
          </div>

          {/* Stego Player */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-slate-300 block">Generated Stego Audio Playback:</span>
            <audio
              controls
              src={`/api/audio/download/${stegoResult.download_id}`}
              className="w-full h-10 rounded-lg"
            />
            <p className="text-[11px] text-slate-400 italic">
              Listen to the audio: the LSB modification is acoustically imperceptible from the original!
            </p>
          </div>

          {/* Metric Breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">PAYLOAD SIZE</span>
              <span className="text-cyan-300 font-bold">{stegoResult.payload_size} Bytes</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">ENVELOPE SIZE</span>
              <span className="text-purple-300 font-bold">{stegoResult.envelope_size} Bytes</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">CAPACITY USED</span>
              <span className="text-emerald-300 font-bold">{stegoResult.capacity_used_pct}%</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-slate-500 block text-[10px]">ENCRYPTION</span>
              <span className="text-amber-300 font-bold">{stegoResult.is_encrypted ? 'AES-GCM' : 'None'}</span>
            </div>
          </div>

          {/* Direct Download Button */}
          <a
            href={`/api/audio/download/${stegoResult.download_id}`}
            download={stegoResult.filename}
            className="w-full py-4 rounded-xl text-sm font-bold text-slate-900 bg-cyan-400 hover:bg-cyan-300 shadow-glow-cyan transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Stego WAV File ({stegoResult.filename})</span>
          </a>
        </div>
      )}
    </div>
  );
}
