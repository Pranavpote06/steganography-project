import React from 'react';
import { ShieldCheck, Plus, SearchCode, Music, Video, RefreshCw } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, sessionStats, onRefreshStats }) {
  const titles = {
    dashboard: 'Dashboard Overview',
    audio: 'Audio Steganography Module',
    video: 'Video Steganography Module',
    extract: 'Hidden Data Recovery & Extraction',
    audit: 'Security Intercepts & Biometric Logs'
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0a0e18]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-white tracking-wide">
          {titles[activeTab] || 'Cyber Steganography'}
        </h2>
        <span className="hidden sm:inline-block text-xs font-mono px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-400 border border-cyan-800/40">
          CYBER-SEC LAB
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* Quick Embed & Extract buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('audio')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 transition-colors"
          >
            <Music className="w-3.5 h-3.5 text-cyan-400" />
            <span>Embed Audio</span>
          </button>

          <button
            onClick={() => setActiveTab('video')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700/60 transition-colors"
          >
            <Video className="w-3.5 h-3.5 text-purple-400" />
            <span>Embed Video</span>
          </button>

          <button
            onClick={() => setActiveTab('extract')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white shadow-glow-cyan transition-all"
          >
            <SearchCode className="w-3.5 h-3.5" />
            <span>Extract Data</span>
          </button>
        </div>

        {/* Live session pill */}
        <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <span className="text-cyan-400">Audio: {sessionStats?.audio_processed ?? 0}</span>
          <span className="text-slate-600">|</span>
          <span className="text-purple-400">Video: {sessionStats?.video_processed ?? 0}</span>
          <button 
            onClick={onRefreshStats} 
            title="Refresh statistics"
            className="ml-1 text-slate-500 hover:text-cyan-400 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>
      </div>
    </header>
  );
}
