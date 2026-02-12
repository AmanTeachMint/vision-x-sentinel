import React, { useState, useEffect } from 'react';
import { getAlerts, getClassrooms } from '../api/client';

const ALERT_LABELS = {
  empty_class: 'Empty Class',
  mischief: 'Mischief',
  loud_noise: 'Loud Noise',
  missing_teacher: 'Missing Teacher',
};

function LogsPanel({ isOpen, onClose }) {
  const [alerts, setAlerts] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [alertsData, classroomsData] = await Promise.all([
        getAlerts(),
        getClassrooms(),
      ]);
      setAlerts(alertsData);
      setClassrooms(classroomsData);
    } catch (err) {
      console.error('Failed to load alerts/classrooms:', err);
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

  const alertsByClassroom = alerts.reduce((acc, alert) => {
    if (!acc[alert.classroom_id]) acc[alert.classroom_id] = [];
    acc[alert.classroom_id].push(alert);
    return acc;
  }, {});

  const sortedClassrooms = [...classrooms].sort((a, b) => {
    const aName = a.name || a.id;
    const bName = b.name || b.id;
    return aName.localeCompare(bName);
  });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Classroom Logs</h2>
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
            {classrooms.length === 0 ? (
              <div className="text-center py-12 text-gray-400">No classrooms found</div>
            ) : (
              <table className="w-full text-left">
                <thead className="border-b border-gray-700">
                  <tr>
                    <th className="pb-2 text-gray-400 font-medium">Classroom</th>
                    <th className="pb-2 text-gray-400 font-medium">Current Status</th>
                    <th className="pb-2 text-gray-400 font-medium">Last Updated</th>
                    <th className="pb-2 text-gray-400 font-medium">Recent Updates</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedClassrooms.map((classroom) => {
                    const recentAlerts = (alertsByClassroom[classroom.id] || [])
                      .slice()
                      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                      .slice(0, 5);
                    return (
                      <tr key={classroom.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                        <td className="py-3 text-sm font-medium">{classroom.name || classroom.id}</td>
                        <td className="py-3 text-sm">
                          <span className="px-2 py-1 bg-gray-700 rounded text-xs capitalize">
                            {classroom.current_status || 'unknown'}
                          </span>
                        </td>
                        <td className="py-3 text-sm">{formatTime(classroom.updated_at)}</td>
                        <td className="py-3 text-sm">
                          <details className="cursor-pointer">
                            <summary className="text-amber-300 hover:text-amber-200">
                              View recent
                            </summary>
                            <div className="mt-2 space-y-2">
                              {recentAlerts.length === 0 ? (
                                <div className="text-xs text-gray-400">No recent alerts</div>
                              ) : (
                                recentAlerts.map((alert) => (
                                  <div key={alert.id} className="text-xs text-gray-300 flex items-center gap-2">
                                    <span className="px-2 py-0.5 bg-gray-700 rounded">
                                      {ALERT_LABELS[alert.type] || alert.type}
                                    </span>
                                    <span className="text-gray-500">{formatTime(alert.timestamp)}</span>
                                  </div>
                                ))
                              )}
                            </div>
                          </details>
                        </td>
                      </tr>
                    );
                  })}
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
