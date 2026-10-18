import React from 'react';
import {
  LayoutDashboard,
  Music,
  Video,
  SearchCode,
  Camera,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, sessionStats }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'audio', label: 'Audio Steganography', icon: Music },
    { id: 'video', label: 'Video Steganography', icon: Video },
    { id: 'extract', label: 'Extract Hidden Data', icon: SearchCode },
    { id: 'audit', label: 'Security Intercepts', icon: Camera },
  ];

  return (
    <aside className="w-64 bg-[#0a0e18]/90 border-r border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0 backdrop-blur-md z-30">
      <div>
        {/* Logo / Brand */}
        <div className="p-6 border-b border-slate-800/60">
          <div className="flex items-center gap-3">
            <img
              src="/logo.jpg"
              alt="Steganography Logo"
              className="w-11 h-11 rounded-xl object-cover border border-cyan-500/40 shadow-glow-cyan"
            />
            <div>
              <h1 className="font-bold text-base tracking-wider bg-gradient-to-r from-cyan-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
                STEGOCYBER
              </h1>
              <p className="text-[11px] text-slate-400 uppercase tracking-widest font-mono">
                Pranav Pote
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/15 to-purple-600/15 text-cyan-300 border border-cyan-500/30 shadow-glow-cyan'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-transform group-hover:scale-110 ${
                      isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-cyan-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono border border-slate-700/50">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer System Badge */}
      <div className="p-4 border-t border-slate-800/60">
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              Engine Online
            </span>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/40">
              AES-GCM
            </span>
          </div>
          <div className="text-[11px] text-slate-400">
            Session Ops: <span className="font-mono text-slate-200 font-semibold">{sessionStats?.total_processed ?? 0}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
