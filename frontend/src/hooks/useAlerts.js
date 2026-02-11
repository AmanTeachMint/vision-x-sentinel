import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { getAlerts } from '../api/client';

const POLL_INTERVAL_MS = 3000;

const ALERT_LABELS = {
  empty_class: 'Empty Class',
  mischief: 'Mischief',
  loud_noise: 'Loud noise',
};

/**
 * Polls GET /api/alerts every 3s, shows a toast for each new alert.
 * Returns { alerts, recentAlertClassroomIds } for optional card indicators.
 */
export function useAlerts() {
  const [alerts, setAlerts] = useState([]);
  const seenIdsRef = useRef(new Set());
  const firstPollDoneRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const list = await getAlerts();
        if (cancelled) return;
        setAlerts(list);

        if (!firstPollDoneRef.current) {
          firstPollDoneRef.current = true;
          list.forEach((a) => a.id && seenIdsRef.current.add(a.id));
          return;
        }

        for (const a of list) {
          const id = a.id;
          if (id && !seenIdsRef.current.has(id)) {
            seenIdsRef.current.add(id);
            const label = ALERT_LABELS[a.type] || a.type;
            const msg = `${label} detected in ${a.classroom_id}`;
            toast(msg, {
              icon: '⚠️',
              duration: 5000,
            });
          }
        }
      } catch (err) {
        if (!cancelled) console.error('Alerts poll failed:', err);
      }
    };

    poll();
    const interval = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  // Classroom IDs that have at least one alert in the current list (for card indicator)
  const recentAlertClassroomIds = [...new Set(alerts.map((a) => a.classroom_id))];

  return { alerts, recentAlertClassroomIds };
}
