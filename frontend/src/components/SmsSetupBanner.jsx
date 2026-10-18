import React, { useState, useEffect } from 'react';
import { Phone, X, CheckCircle, AlertCircle, ExternalLink, Settings } from 'lucide-react';
import { getSmsStatus } from '../api';

export default function SmsSetupBanner({ onNavigateToConfig }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const data = await getSmsStatus();
      setStatus(data);
    } catch (err) {
      console.warn("Could not check SMS status:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || dismissed) return null;
  
  // Don't show if SMS is already configured
  if (status?.active_provider && status.active_provider !== 'none') return null;

  return (
    <div className="mb-6 relative">
      <div className="bg-gradient-to-r from-amber-900/40 to-orange-900/40 border border-amber-500/30 rounded-xl p-4 backdrop-blur-sm">
        <button
          onClick={() => setDismissed(true)}
          className="absolute top-3 right-3 text-amber-300/60 hover:text-amber-300 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="w-6 h-6 text-amber-400" />
          </div>

          <div className="flex-1 pr-8">
            <h3 className="text-lg font-semibold text-amber-100 mb-2 flex items-center gap-2">
              <Phone className="w-5 h-5" />
              SMS Gateway Not Configured
            </h3>
            
            <p className="text-sm text-amber-200/80 mb-4 leading-relaxed">
              Real SMS delivery to phone numbers is not set up yet. Recipients will see OTP codes in the browser instead of receiving actual text messages. 
              <strong className="text-amber-100"> Configure Twilio or Fast2SMS</strong> to send real OTP codes via SMS.
            </p>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={onNavigateToConfig}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-all duration-200 text-sm font-medium shadow-lg hover:shadow-amber-500/25"
              >
                <Settings className="w-4 h-4" />
                Configure SMS Now
              </button>

              <a
                href="/QUICKSTART_SMS.md"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-all duration-200 text-sm font-medium border border-slate-600/50"
              >
                <ExternalLink className="w-4 h-4" />
                Quick Setup Guide (5 min)
              </a>
            </div>

            <div className="mt-4 pt-4 border-t border-amber-500/20">
              <p className="text-xs text-amber-300/60">
                💡 <strong>Recommended:</strong> Twilio (free $15 credit, worldwide delivery) • 
                <strong> Budget India:</strong> Fast2SMS (₹0.15/SMS)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
