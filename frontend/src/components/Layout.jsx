import React, { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import LogsPanel from './LogsPanel';
import { getAdminProfile } from '../api/client';

function Layout({ children, activeCount = 0, inactiveCount = 0, onRefresh, onSearchChange, searchValue = '' }) {
  const [logsOpen, setLogsOpen] = useState(false);
  const [adminProfile, setAdminProfile] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    getAdminProfile()
      .then((profile) => setAdminProfile(profile))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const handleClick = (e) => {
      if (!profileRef.current) return;
      if (!profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, []);

  const handleBroadcast = () => {
    toast.success('Broadcast sent to all classrooms');
  };

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      {/* Header */}
      <header className="bg-dark-card border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Vision X Sentinel</h1>
        <div className="flex items-center gap-3" ref={profileRef}>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-100">{adminProfile?.name || 'Admin'}</div>
            <div className="text-xs text-gray-400">{adminProfile?.email || 'admin@school.org'}</div>
          </div>
          <button
            onClick={() => setProfileOpen((v) => !v)}
            className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold"
            aria-label="Admin profile"
          >
            {(adminProfile?.avatar_initials || 'AD').slice(0, 2)}
          </button>
          {profileOpen && (
            <div className="absolute right-6 top-16 bg-dark-card border border-gray-700 rounded-md shadow-lg w-40 z-50">
              <button
                onClick={() => {
                  setProfileOpen(false);
                  toast.success('Logged out');
                }}
                className="w-full text-left px-4 py-2 text-sm text-gray-200 hover:bg-gray-800 flex items-center gap-2"
              >
                <svg
                  className="w-4 h-4 text-gray-300"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M15 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M10 17l5-5-5-5"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M15 12H8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Logout
              </button>
            </div>
          )}
        </div>
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
