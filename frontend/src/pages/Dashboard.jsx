import React, { useState } from 'react';
import { 
  Activity, 
  Music, 
  Video, 
  SearchCode, 
  FileText, 
  Lock, 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  Layers,
  Sparkles
} from 'lucide-react';
import { resetStats } from '../api';

export default function Dashboard({ sessionStats, onRefreshStats, setActiveTab, showToast }) {
  const [isResetting, setIsResetting] = useState(false);

  const handleReset = async () => {
    if (!window.confirm("Are you sure you want to reset all session statistics and operation history?")) {
      return;
    }
    try {
      setIsResetting(true);
      await resetStats();
      await onRefreshStats();
      showToast({ type: 'success', title: 'Session Cleared', message: 'All operation logs and metrics have been reset.' });
    } catch (err) {
      showToast({ type: 'error', title: 'Reset Failed', message: err.message });
    } finally {
      setIsResetting(false);
    }
  };

  const statCards = [
    {
      title: 'Total Processed',
      value: sessionStats?.total_processed ?? 0,
      icon: Activity,
      desc: 'Operations this session',
      color: 'from-cyan-500/20 to-blue-500/20',
      border: 'border-cyan-500/30',
      text: 'text-cyan-400'
    },
    {
      title: 'Audio Operations',
      value: sessionStats?.audio_processed ?? 0,
      icon: Music,
      desc: `${sessionStats?.audio_embeds ?? 0} Embeds • ${sessionStats?.audio_extracts ?? 0} Extracts`,
      color: 'from-purple-500/20 to-pink-500/20',
      border: 'border-purple-500/30',
      text: 'text-purple-400'
    },
    {
      title: 'Video Operations',
      value: sessionStats?.video_processed ?? 0,
      icon: Video,
      desc: `${sessionStats?.video_embeds ?? 0} Embeds • ${sessionStats?.video_extracts ?? 0} Extracts`,
      color: 'from-pink-500/20 to-rose-500/20',
      border: 'border-pink-500/30',
      text: 'text-pink-400'
    },
    {
      title: 'Security Cipher',
      value: 'AES-256-GCM',
      icon: Lock,
      desc: 'PBKDF2 100k Iterations',
      color: 'from-emerald-500/20 to-teal-500/20',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400'
    }
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#0d1627] via-[#121128] to-[#1a0f26] border border-cyan-500/20 p-8 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 text-xs font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            Cybersecurity Data Concealment Platform
          </div>

          <h2 className="text-3xl font-extrabold text-white tracking-tight leading-tight">
            Next-Gen Media Steganography & Encrypted Extraction
          </h2>

          <p className="text-slate-300 text-sm leading-relaxed">
            Conceal classified text or confidential files inside uncompressed audio waveforms and video frame pixels 
            using high-fidelity Least Significant Bit (LSB) embedding with authenticated AES-256-GCM encryption.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setActiveTab('audio')}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 shadow-glow-cyan transition-all flex items-center gap-2"
            >
              <Music className="w-4 h-4" />
              <span>Embed Audio</span>
            </button>

            <button
              onClick={() => setActiveTab('video')}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 shadow-glow-purple transition-all flex items-center gap-2"
            >
              <Video className="w-4 h-4" />
              <span>Embed Video</span>
            </button>

            <button
              onClick={() => setActiveTab('extract')}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-200 bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/60 transition-all flex items-center gap-2"
            >
              <SearchCode className="w-4 h-4 text-cyan-400" />
              <span>Extract Data</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real Session Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-6 rounded-2xl bg-gradient-to-br ${card.color} border ${card.border} backdrop-blur-md shadow-lg flex flex-col justify-between`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  {card.title}
                </span>
                <div className={`p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 ${card.text}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold font-mono text-white mb-1">
                  {card.value}
                </div>
                <div className="text-xs text-slate-400">{card.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Session Operations Table */}
      <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-bold text-white">Live Session Operations</h3>
              <p className="text-xs text-slate-400">Actual operations executed during this server session</p>
            </div>
          </div>

          {sessionStats?.recent_operations?.length > 0 && (
            <button
              onClick={handleReset}
              disabled={isResetting}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 border border-slate-800 transition-colors flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Log</span>
            </button>
          )}
        </div>

        {(!sessionStats?.recent_operations || sessionStats.recent_operations.length === 0) ? (
          <div className="p-8 text-center rounded-xl bg-slate-950/40 border border-slate-800/60">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-900 flex items-center justify-center text-slate-500">
              <Layers className="w-6 h-6" />
            </div>
            <p className="text-sm text-slate-400 font-medium">No operations recorded yet in this session</p>
            <p className="text-xs text-slate-500 mt-1">
              Embed or extract confidential data using the Audio or Video modules to track live operations.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Time</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Carrier Media</th>
                  <th className="py-3 px-4">Payload Target</th>
                  <th className="py-3 px-4">Encryption</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {sessionStats.recent_operations.map((op) => (
                  <tr key={op.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 text-slate-500 text-[11px]">
                      {new Date(op.timestamp * 1000).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        op.op_type === 'embed'
                          ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/50'
                          : 'bg-purple-950/80 text-purple-300 border border-purple-800/50'
                      }`}>
                        {op.op_type} ({op.media_type})
                      </span>
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-200 truncate max-w-[150px]">
                      {op.media_name}
                    </td>
                    <td className="py-3 px-4 text-slate-400 truncate max-w-[150px]">
                      {op.payload_name}
                    </td>
                    <td className="py-3 px-4">
                      {op.encrypted ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px]">
                          <Lock className="w-3 h-3" />
                          AES-GCM
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[11px]">Plain</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {op.success ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Success
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-400">
                          <XCircle className="w-3.5 h-3.5" />
                          Failed
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
