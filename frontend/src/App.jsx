import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Toast from './components/Toast';
import Dashboard from './pages/Dashboard';
import AudioStego from './pages/AudioStego';
import VideoStego from './pages/VideoStego';
import ExtractData from './pages/ExtractData';
import AuditLogs from './pages/AuditLogs';
import { getStats } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sessionStats, setSessionStats] = useState(null);
  const [toast, setToast] = useState(null);

  const fetchSessionStats = async () => {
    try {
      const stats = await getStats();
      setSessionStats(stats);
    } catch (err) {
      console.error('Failed to load session statistics:', err);
    }
  };

  useEffect(() => {
    fetchSessionStats();
    // Refresh stats every 15 seconds
    const interval = setInterval(fetchSessionStats, 15000);
    return () => clearInterval(interval);
  }, []);

  const showToast = ({ type = 'info', title, message }) => {
    setToast({ type, title, message });
  };

  return (
    <div className="flex min-h-screen bg-[#07090e] text-slate-100 cyber-grid">
      {/* Toast Notification Container */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Persistent Cyber Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        sessionStats={sessionStats}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          sessionStats={sessionStats}
          onRefreshStats={fetchSessionStats}
        />

        <main className="flex-1 p-6 sm:p-8 lg:p-10">
          {activeTab === 'dashboard' && (
            <Dashboard
              sessionStats={sessionStats}
              onRefreshStats={fetchSessionStats}
              setActiveTab={setActiveTab}
              showToast={showToast}
            />
          )}

          {activeTab === 'audio' && (
            <AudioStego
              showToast={showToast}
              onOperationComplete={fetchSessionStats}
            />
          )}

          {activeTab === 'video' && (
            <VideoStego
              showToast={showToast}
              onOperationComplete={fetchSessionStats}
            />
          )}

          {activeTab === 'extract' && (
            <ExtractData
              showToast={showToast}
              onOperationComplete={fetchSessionStats}
            />
          )}

          {activeTab === 'audit' && (
            <AuditLogs showToast={showToast} />
          )}
        </main>
      </div>
    </div>
  );
}
