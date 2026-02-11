import React, { useState, useEffect } from 'react';
import { getAlerts } from '../api/client';

const ALERT_LABELS = {
  empty_class: 'Empty Class',
  mischief: 'Mischief',
  loud_noise: 'Loud Noise',
};

function LogsPanel({ isOpen, onClose }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadAlerts();
    }
  }, [isOpen]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await getAlerts();
      setAlerts(data.slice(0, 20));
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Alert Logs</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-400">Loading alerts...</div>
          </div>
        ) : (
          <div className="overflow-y-auto flex-1">
            {alerts.length === 0 ? (
              <div className="text-center py-12 text-gray-400">No alerts found</div>
            ) : (
              <table className="w-full text-left">
                <thead className="border-b border-gray-700">
                  <tr>
                    <th className="pb-2 text-gray-400 font-medium">Time</th>
                    <th className="pb-2 text-gray-400 font-medium">Classroom</th>
                    <th className="pb-2 text-gray-400 font-medium">Type</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                      <td className="py-3 text-sm">{formatTime(alert.timestamp)}</td>
                      <td className="py-3 text-sm font-medium">{alert.classroom_id}</td>
                      <td className="py-3 text-sm">
                        <span className="px-2 py-1 bg-gray-700 rounded text-xs">
                          {ALERT_LABELS[alert.type] || alert.type}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default LogsPanel;
