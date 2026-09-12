import { useEffect, useState } from 'react';
import { BASE } from '../services/api';

export function useSSE() {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const es = new EventSource(`${BASE}/api/live/stream`);
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.addEventListener('connected', (e) => {
      setEvents(prev => [...prev.slice(-20), {type:'connected', data: JSON.parse(e.data), time: Date.now()}]);
    });
    es.addEventListener('heartbeat', (e) => {
      setEvents(prev => [...prev.slice(-20), {type:'heartbeat', data: JSON.parse(e.data), time: Date.now()}]);
    });
    es.addEventListener('advisory_update', (e) => {
      setEvents(prev => [...prev.slice(-20), {type:'advisory_update', data: JSON.parse(e.data), time: Date.now()}]);
    });
    es.addEventListener('risk_change', (e) => {
      setEvents(prev => [...prev.slice(-20), {type:'risk_change', data: JSON.parse(e.data), time: Date.now()}]);
    });
    return () => es.close();
  }, []);

  return { events, connected };
}
