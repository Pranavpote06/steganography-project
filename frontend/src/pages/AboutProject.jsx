import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Terminal, 
  Server, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  ExternalLink,
  Code2,
  FileCheck2,
  Lock,
  Layers
} from 'lucide-react';
import { getHealth } from '../api';

export default function AboutProject() {
  const [healthData, setHealthData] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  const checkStatus = async () => {
    try {
      setLoadingHealth(true);
      const data = await getHealth();
      setHealthData(data);
    } catch (err) {
      setHealthData({ status: 'unreachable', error: err.message });
    } finally {
      setLoadingHealth(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const stackItems = [
    { name: 'React 18 & Vite', category: 'Frontend UI', desc: 'Ultra-fast SPA build with modern hook architecture' },
    { name: 'Tailwind CSS', category: 'Styling', desc: 'Cyberpunk responsive design with custom neon accents' },
    { name: 'Python 3.12 & FastAPI', category: 'Backend Framework', desc: 'High-performance asynchronous REST API' },
    { name: 'OpenCV (cv2)', category: 'Computer Vision', desc: 'Frame extraction and spatial pixel matrix manipulation' },
    { name: 'FFmpeg 9.0.1 (Gyan)', category: 'Media Reassembly', desc: 'Lossless RGB video encoding & audio multiplexing' },
    { name: 'SciPy & SoundFile', category: 'Signal Processing', desc: 'PCM WAV sample reading and waveform LSB writing' },
    { name: 'Cryptography (AES-GCM)', category: 'Data Security', desc: 'Authenticated symmetric cipher with PBKDF2 key derivation' },
    { name: 'Pytest & HTTPX', category: 'Testing Suite', desc: 'Comprehensive test coverage across media & crypto layers' },
  ];

  return (
    <div className="space-y-10 max-w-5xl mx-auto animate-fade-in pb-16">
      {/* Page Header */}
      <div className="border-b border-slate-800/80 pb-6">
        <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
          <ShieldCheck className="w-5 h-5" />
          <span className="text-xs font-mono font-semibold tracking-wider uppercase">System Architecture</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">About Project & System Status</h2>
        <p className="text-sm text-slate-300 mt-2 max-w-3xl leading-relaxed">
          Production-grade cybersecurity tool built for covert data transmission and steganalysis education.
        </p>
      </div>

      {/* Live System Diagnostics Box */}
      <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-bold text-white">Live Backend Diagnostics</h3>
              <p className="text-xs text-slate-400">Real-time health check against /api/health</p>
            </div>
          </div>

          <button
            onClick={checkStatus}
            disabled={loadingHealth}
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingHealth ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Check Diagnostics</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 block uppercase">API Health Status</span>
            {healthData?.status === 'healthy' ? (
              <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Healthy & Online
              </span>
            ) : (
              <span className="text-rose-400 font-bold flex items-center gap-1.5">
                <XCircle className="w-4 h-4" /> Offline / Error
              </span>
            )}
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 block uppercase">FFmpeg Executable</span>
            <span className="text-cyan-300 font-bold truncate block" title={healthData?.ffmpeg_path}>
              {healthData?.ffmpeg_available ? 'Detected & Operational' : 'Missing'}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-500 block uppercase">Python Runtime</span>
            <span className="text-purple-300 font-bold truncate block">
              {healthData?.python_version ? healthData.python_version.split(' ')[0] : 'Python 3.12'}
            </span>
          </div>
        </div>
      </div>

      {/* Tech Stack Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-purple-400" />
          Technology Stack
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stackItems.map((item, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-100">{item.name}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700/60">
                  {item.category}
                </span>
              </div>
              <p className="text-xs text-slate-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Security Principles & Disclosures */}
      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3 text-xs text-slate-300">
        <h4 className="font-bold text-white text-sm flex items-center gap-2">
          <Lock className="w-4 h-4 text-emerald-400" />
          Security Disclosures & Data Privacy
        </h4>
        <p className="leading-relaxed text-slate-400">
          This system is engineered with privacy-by-design. Media processing occurs strictly on the local backend server. 
          No user files, secret messages, or passwords are transmitted to third-party clouds or external telemetry endpoints. 
          All temporary carrier and stego files are stored in an isolated upload cache and scrubbed automatically.
        </p>
      </div>
    </div>
  );
}
