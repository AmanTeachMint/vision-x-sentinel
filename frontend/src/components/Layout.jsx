import React, { useState } from 'react';
import toast from 'react-hot-toast';
import LogsPanel from './LogsPanel';

function Layout({ children, activeCount = 0, inactiveCount = 0, onRefresh, onSearchChange, searchValue = '' }) {
  const [logsOpen, setLogsOpen] = useState(false);

  const handleBroadcast = () => {
    toast.success('Broadcast sent to all classrooms');
  };

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      {/* Header */}
      <header className="bg-dark-card border-b border-gray-700 px-6 py-4">
        <h1 className="text-2xl font-bold">Vision X Sentinel</h1>
      </header>

      {/* Top bar: Search, Logs, Broadcast */}
      <div className="bg-dark-card border-b border-gray-700 px-6 py-3 flex items-center gap-4">
        <input
          type="text"
          placeholder="Search by room name"
          value={searchValue}
          onChange={(e) => onSearchChange?.(e.target.value)}
          className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => setLogsOpen(true)}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors flex items-center gap-2"
        >
          <span>📋</span>
          <span>Logs</span>
        </button>
        <button
          onClick={handleBroadcast}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors flex items-center gap-2"
        >
          <span>📢</span>
          <span>Broadcast</span>
        </button>
      </div>

      {/* Main content */}
      <main className="p-6">
        {children}
      </main>

      {/* Footer/Status bar */}
      <footer className="bg-dark-card border-t border-gray-700 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-green-500 rounded-full"></span>
            <span>Active {activeCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
            <span>Inactive {inactiveCount}</span>
          </div>
        </div>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors flex items-center gap-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </footer>

      <LogsPanel isOpen={logsOpen} onClose={() => setLogsOpen(false)} />
    </div>
  );
}

export default Layout;
