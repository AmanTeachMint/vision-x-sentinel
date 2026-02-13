import React, { useState, useEffect } from 'react';
import { getAlerts, getClassrooms } from '../api/client';

const ALERT_LABELS = {
  empty_class: 'Empty Class',
  mischief: 'Mischief',
  loud_noise: 'Loud Noise',
};

function LogsPanel({ isOpen, onClose }) {
  const [alerts, setAlerts] = useState([]);
  const [classroomNames, setClassroomNames] = useState({});
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
      setAlerts(alertsData.slice(0, 20));
      const nameMap = classroomsData.reduce((acc, c) => {
        acc[c.id] = c.name;
        return acc;
      }, {});
      setClassroomNames(nameMap);
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

  // Group alerts by classroom; within each group newest first
  const alertsByClass = React.useMemo(() => {
    const groups = {};
    alerts.forEach((alert) => {
      const id = alert.classroom_id;
      if (!groups[id]) groups[id] = [];
      groups[id].push(alert);
    });
    Object.keys(groups).forEach((id) => {
      groups[id].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    });
    return Object.keys(groups)
      .sort((a, b) => (classroomNames[a] || a).localeCompare(classroomNames[b] || b))
      .map((classroomId) => ({
        classroomId,
        classroomName: classroomNames[classroomId] || classroomId,
        alerts: groups[classroomId],
      }));
  }, [alerts, classroomNames]);

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
            {alertsByClass.length === 0 ? (
              <div className="text-center py-12 text-gray-400">No alerts found</div>
            ) : (
              <div className="space-y-6">
                {alertsByClass.map(({ classroomId, classroomName, alerts: classAlerts }) => (
                  <div key={classroomId} className="border border-gray-700 rounded-lg overflow-hidden">
                    <div className="px-4 py-2.5 bg-gray-800/80 border-b border-gray-700 font-medium text-white">
                      {classroomName}
                      <span className="ml-2 text-gray-400 font-normal text-sm">
                        ({classAlerts.length} alert{classAlerts.length !== 1 ? 's' : ''})
                      </span>
                    </div>
                    <table className="w-full text-left">
                      <thead className="bg-gray-800/50">
                        <tr>
                          <th className="px-4 py-2 text-gray-400 font-medium text-sm">Time</th>
                          <th className="px-4 py-2 text-gray-400 font-medium text-sm">Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        {classAlerts.map((alert) => (
                          <tr key={alert.id} className="border-t border-gray-700/50 hover:bg-gray-800/50">
                            <td className="px-4 py-2.5 text-sm">{formatTime(alert.timestamp)}</td>
                            <td className="px-4 py-2.5 text-sm">
                              <span className="px-2 py-1 bg-gray-700 rounded text-xs">
                                {ALERT_LABELS[alert.type] || alert.type}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
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
