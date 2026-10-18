import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  CheckCircle2, 
  XCircle, 
  Phone, 
  Globe, 
  RefreshCw, 
  Key, 
  Save, 
  AlertTriangle, 
  ExternalLink,
  ShieldCheck,
  Send,
  Sparkles
} from 'lucide-react';
import { getSmsStatus, updateSmsConfig } from '../api';

export default function SMSConfig({ showToast }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState(null);
  
  // Form states
  const [fast2smsKey, setFast2smsKey] = useState('');
  const [twilioSid, setTwilioSid] = useState('');
  const [twilioToken, setTwilioToken] = useState('');
  const [twilioFrom, setTwilioFrom] = useState('');
  const [twofactorKey, setTwofactorKey] = useState('');

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await getSmsStatus();
      setStatus(data);
      if (data.twilio_number) {
        setTwilioFrom(data.twilio_number);
      }
    } catch (err) {
      if (showToast) {
        showToast({ type: 'error', title: 'Status Error', message: 'Could not fetch SMS gateway status.' });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleSave = async (e) => {
    e?.preventDefault();
    try {
      setSaving(true);
      const res = await updateSmsConfig({
        fast2smsKey: fast2smsKey || undefined,
        twilioSid: twilioSid || undefined,
        twilioToken: twilioToken || undefined,
        twilioFrom: twilioFrom || undefined,
        twofactorKey: twofactorKey || undefined
      });

      if (showToast) {
        showToast({
          type: 'success',
          title: 'SMS Gateway Configured',
          message: `Active Gateway: ${res.active_provider ? res.active_provider.toUpperCase() : 'NONE'}. OTP codes will now be sent via real cellular SMS.`
        });
      }
      await loadStatus();
    } catch (err) {
      if (showToast) {
        showToast({
          type: 'error',
          title: 'Configuration Error',
          message: err.response?.data?.detail || err.message || 'Failed to save SMS credentials'
        });
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2.5 text-cyan-400 mb-1">
            <MessageSquare className="w-5 h-5" />
            <span className="text-xs font-mono font-semibold tracking-wider uppercase">Cellular SMS Subsystem</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">SMS Gateway Configuration</h2>
          <p className="text-sm text-slate-400 mt-1">
            Connect Fast2SMS or Twilio to transmit real OTP security codes directly to recipient physical mobile SIM cards.
          </p>
        </div>

        <button
          onClick={loadStatus}
          disabled={loading}
          className="self-start sm:self-auto px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-900 border border-slate-700/80 transition-colors flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      {/* Gateway Status Summary Card */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider">
            Operational Gateway Status
          </span>
          <span
            className={`text-xs font-mono font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 ${
              status?.active_provider && status.active_provider !== 'none'
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/60'
                : 'bg-amber-950/80 text-amber-300 border-amber-500/60'
            }`}
          >
            {status?.active_provider && status.active_provider !== 'none' ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ACTIVE: {status.active_provider.toUpperCase()} (Live SMS Ready)
              </>
            ) : (
              <>
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                NO ACTIVE GATEWAY (Configure below)
              </>
            )}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          {/* Fast2SMS */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-white flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5 text-purple-400" /> Fast2SMS (India)
              </div>
              <span className="text-[11px] text-slate-400 font-mono">Route: OTP & Quick SMS</span>
            </div>
            {status?.fast2sms_configured ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <XCircle className="w-5 h-5 text-slate-600" />
            )}
          </div>

          {/* Twilio */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-white flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-cyan-400" /> Twilio (Global)
              </div>
              <span className="text-[11px] text-slate-400 font-mono">
                {status?.twilio_number ? status.twilio_number : 'Worldwide Delivery'}
              </span>
            </div>
            {status?.twilio_configured ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <XCircle className="w-5 h-5 text-slate-600" />
            )}
          </div>

          {/* 2Factor.in */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-white flex items-center gap-1.5">
                <Send className="w-3.5 h-3.5 text-blue-400" /> 2Factor.in (India)
              </div>
              <span className="text-[11px] text-slate-400 font-mono">Direct Telco Carrier</span>
            </div>
            {status?.twofactor_configured ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <XCircle className="w-5 h-5 text-slate-600" />
            )}
          </div>
        </div>
      </div>

      {/* Provider Options */}
      <form onSubmit={handleSave} className="space-y-6">
        {/* OPTION 1: Fast2SMS (Recommended for India) */}
        <div className="p-6 rounded-2xl bg-purple-950/20 border border-purple-500/40 space-y-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-purple-950 border border-purple-800 text-purple-400">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Option 1: Fast2SMS (India +91)
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                    Recommended for India
                  </span>
                </h3>
                <p className="text-xs text-slate-400">
                  Direct cellular delivery to Indian mobile numbers. Free wallet credits available on signup.
                </p>
              </div>
            </div>

            <a
              href="https://www.fast2sms.com"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 underline font-mono"
            >
              <span>Get API Key</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-mono text-purple-300 uppercase tracking-wider">
              Fast2SMS Authorization API Key
            </label>
            <div className="relative">
              <input
                type="password"
                value={fast2smsKey}
                onChange={(e) => setFast2smsKey(e.target.value)}
                placeholder={status?.fast2sms_configured ? "•••••••••••••••••••••••••••••••• (Configured)" : "Paste your Fast2SMS Authorization key here..."}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-purple-500 font-mono transition-colors"
              />
              <Key className="w-4 h-4 text-purple-400 absolute left-3.5 top-3.5" />
            </div>
            <p className="text-[11px] text-slate-500">
              Get key from: fast2sms.com → Dashboard → Dev API → Authorization Key
            </p>
          </div>
        </div>

        {/* OPTION 2: Twilio (Worldwide) */}
        <div className="p-6 rounded-2xl bg-cyan-950/20 border border-cyan-500/40 space-y-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Option 2: Twilio (Global / International)
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                    Worldwide
                  </span>
                </h3>
                <p className="text-xs text-slate-400">
                  Sends live cellular SMS anywhere in the world. Free trial provides $15 credit.
                </p>
              </div>
            </div>

            <a
              href="https://www.twilio.com"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 underline font-mono"
            >
              <span>Get Twilio Account</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-mono text-cyan-300 uppercase tracking-wider">
                Account SID
              </label>
              <input
                type="text"
                value={twilioSid}
                onChange={(e) => setTwilioSid(e.target.value)}
                placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-mono text-cyan-300 uppercase tracking-wider">
                Auth Token
              </label>
              <input
                type="password"
                value={twilioToken}
                onChange={(e) => setTwilioToken(e.target.value)}
                placeholder="Enter auth token..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-mono text-cyan-300 uppercase tracking-wider">
              Twilio Phone Number (Sender)
            </label>
            <input
              type="text"
              value={twilioFrom}
              onChange={(e) => setTwilioFrom(e.target.value)}
              placeholder="e.g. +12025550143"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
            />
          </div>
        </div>

        {/* OPTION 3: 2Factor.in */}
        <div className="p-6 rounded-2xl bg-blue-950/20 border border-blue-500/40 space-y-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-blue-950 border border-blue-800 text-blue-400">
                <Send className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Option 3: 2Factor.in (India Alternative)
                </h3>
                <p className="text-xs text-slate-400">
                  Alternative Indian transactional SMS provider for instant OTP delivery.
                </p>
              </div>
            </div>

            <a
              href="https://2factor.in"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 underline font-mono"
            >
              <span>2Factor.in</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-mono text-blue-300 uppercase tracking-wider">
              2Factor API Key
            </label>
            <input
              type="password"
              value={twofactorKey}
              onChange={(e) => setTwofactorKey(e.target.value)}
              placeholder="Enter 2Factor API Key..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono transition-colors"
            />
          </div>
        </div>

        {/* Save Action Bar */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3.5 rounded-xl text-sm font-bold uppercase tracking-wider text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 shadow-glow-cyan transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                <span>Saving Credentials...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save SMS Configuration</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
