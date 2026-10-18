import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Camera, 
  Clock, 
  FileText, 
  RotateCcw, 
  UserCheck, 
  ExternalLink, 
  RefreshCw,
  Search,
  CheckCircle2,
  AlertTriangle,
  Download,
  X
} from 'lucide-react';
import { getAuditLogs, clearAuditLogs } from '../api';

export default function AuditLogs({ showToast }) {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const fetchLogs = async () => {
    try {
      setIsLoading(true);
      const res = await getAuditLogs();
      setLogs(res.logs || []);
    } catch (err) {
      showToast({ type: 'error', title: 'Fetch Error', message: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleClear = async () => {
    if (!window.confirm("Are you sure you want to clear all security intercepts and purge captured face photos?")) {
      return;
    }
    try {
      await clearAuditLogs();
      await fetchLogs();
      showToast({ type: 'success', title: 'Audit Vault Cleared', message: 'All intercepted access photos and logs have been wiped.' });
    } catch (err) {
      showToast({ type: 'error', title: 'Clear Failed', message: err.message });
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto animate-fade-in pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
            <Camera className="w-5 h-5" />
            <span className="text-xs font-mono font-semibold tracking-wider uppercase">Sender Intelligence & Audit Vault</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Access Intercepts & Captured Face Scans</h2>
          <p className="text-sm text-slate-400 mt-1">
            Review live biometric face photos and phone numbers of recipients who unlocked your steganographic files.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchLogs}
            disabled={isLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/60 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Refresh Vault</span>
          </button>

          {logs.length > 0 && (
            <button
              onClick={handleClear}
              className="px-3.5 py-2 rounded-xl text-xs font-medium text-rose-300 hover:text-rose-100 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 transition-colors flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Purge Intercepts</span>
            </button>
          )}
        </div>
      </div>

      {/* Logs Grid */}
      {logs.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-slate-900/30 border border-slate-800/80 space-y-3">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
            <UserCheck className="w-8 h-8 opacity-60" />
          </div>
          <h3 className="text-base font-bold text-slate-200">No Biometric Unlocks Recorded Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            When you embed confidential files with <strong>Recipient Verification</strong> enabled, 
            the recipient's captured webcam face photo and phone verification timestamp will appear here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {logs.map((log) => (
            <div
              key={log.id}
              className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 transition-all shadow-lg space-y-4"
            >
              <div className="flex items-start gap-4">
                {/* Captured Face Photo Thumbnail */}
                <div className="relative shrink-0">
                  {log.has_face_capture && log.face_image_url ? (
                    <div 
                      onClick={() => setSelectedImage(log.face_image_url)}
                      className="w-24 h-24 rounded-xl overflow-hidden bg-black border-2 border-cyan-500/60 shadow-glow-cyan cursor-pointer group relative"
                    >
                      <img
                        src={log.face_image_url}
                        alt="Captured Recipient Face"
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                      />
                      <div className="absolute inset-0 bg-cyan-950/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                        <span className="text-[10px] text-cyan-300 font-mono font-bold">VIEW FULL</span>
                      </div>
                    </div>
                  ) : (
                    <div className="w-24 h-24 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-600">
                      <Camera className="w-8 h-8" />
                    </div>
                  )}
                  <span className="absolute -bottom-2 -right-1 px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-600 text-[9px] font-mono text-emerald-300 flex items-center gap-1">
                    <CheckCircle2 className="w-2.5 h-2.5" /> VERIFIED
                  </span>
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-cyan-400 truncate">
                      {log.recipient_phone || 'Biometric Intercept'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {log.formatted_time.split(' ')[1]}
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 truncate font-semibold">
                    File: <span className="text-white font-mono">{log.carrier_filename}</span>
                  </div>

                  <div className="text-[11px] text-slate-400 truncate">
                    Payload: <span className="text-purple-300">{log.payload_name}</span> ({log.payload_type})
                  </div>

                  <div className="text-[10px] text-slate-500 font-mono pt-1">
                    Sender ID: <span className="text-slate-300">{log.sender_id}</span>
                  </div>
                </div>
              </div>

              {/* Status bar */}
              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  2FA & Biometric Authenticated
                </span>
                <span>{log.formatted_time.split(' ')[0]}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Full-Screen Captured Face Photo Modal */}
      {selectedImage && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in">
          <div className="relative max-w-lg w-full bg-slate-950 border border-cyan-500/60 rounded-3xl p-6 shadow-glow-cyan space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400">
                <Camera className="w-5 h-5" />
                <h4 className="text-sm font-bold text-white tracking-wide">Captured Recipient Biometric Face Scan</h4>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="aspect-square rounded-2xl overflow-hidden bg-black border border-slate-800 relative">
              <img
                src={selectedImage}
                alt="Enlarged Face Capture"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-3 left-3 bg-slate-950/80 px-3 py-1 rounded-full border border-cyan-500/40 text-[11px] font-mono text-cyan-300">
                ORIGINAL LIVE CAPTURE • 100% UNEDITED
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <a
                href={selectedImage}
                download="recipient_face_capture.jpg"
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-900 bg-cyan-400 hover:bg-cyan-300 transition-colors flex items-center gap-1.5"
              >
                <Download className="w-4 h-4" />
                <span>Download Photo</span>
              </a>
              <button
                onClick={() => setSelectedImage(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 bg-slate-900 hover:bg-slate-800 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
