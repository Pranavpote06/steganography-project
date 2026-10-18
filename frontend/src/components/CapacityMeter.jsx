import React from 'react';
import { Gauge, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function CapacityMeter({ 
  capacityBytes = 0, 
  payloadBytes = 0,
  details = {} 
}) {
  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const percentage = capacityBytes > 0 
    ? Math.min(100, Math.max(0, (payloadBytes / capacityBytes) * 100))
    : 0;

  const isExceeded = payloadBytes > capacityBytes && capacityBytes > 0;
  
  let barColor = 'from-cyan-500 to-blue-500';
  let badgeColor = 'text-cyan-400 bg-cyan-950/60 border-cyan-800/40';

  if (isExceeded) {
    barColor = 'from-rose-500 to-red-600';
    badgeColor = 'text-rose-400 bg-rose-950/60 border-rose-800/40';
  } else if (percentage > 75) {
    barColor = 'from-amber-500 to-orange-500';
    badgeColor = 'text-amber-400 bg-amber-950/60 border-amber-800/40';
  } else if (percentage > 0) {
    barColor = 'from-emerald-400 to-cyan-500';
    badgeColor = 'text-emerald-400 bg-emerald-950/60 border-emerald-800/40';
  }

  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Steganographic Carrier Capacity
          </span>
        </div>
        <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${badgeColor}`}>
          {isExceeded ? 'CAPACITY EXCEEDED' : `${percentage.toFixed(2)}% ALLOCATED`}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2.5 rounded-full bg-slate-800/90 overflow-hidden relative">
        <div
          className={`h-full bg-gradient-to-r ${barColor} transition-all duration-500 ease-out`}
          style={{ width: `${Math.min(100, percentage)}%` }}
        />
      </div>

      {/* Metric Breakdown */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono text-slate-400 pt-1">
        <div>
          <span className="text-[10px] text-slate-500 block">CARRIER CAPACITY</span>
          <span className="text-slate-200 font-semibold">{formatSize(capacityBytes)}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 block">PAYLOAD REQ.</span>
          <span className={isExceeded ? "text-rose-400 font-semibold" : "text-cyan-300 font-semibold"}>
            {formatSize(payloadBytes)}
          </span>
        </div>
        {details.duration_seconds !== undefined && (
          <div>
            <span className="text-[10px] text-slate-500 block">MEDIA DURATION</span>
            <span className="text-slate-200 font-semibold">{details.duration_seconds}s</span>
          </div>
        )}
      </div>

      {isExceeded && (
        <div className="flex items-center gap-2 text-xs text-rose-400 bg-rose-950/40 p-2.5 rounded-lg border border-rose-800/50">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Payload exceeds carrier capacity. Choose a larger carrier media or reduce payload size.</span>
        </div>
      )}
    </div>
  );
}
