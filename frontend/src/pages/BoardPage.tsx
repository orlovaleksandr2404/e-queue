import { useEffect, useRef, useState } from 'react';
import { getBoardTickets, type BoardTicket } from '../api/board';
import { getWindows } from '../api/windows';

interface WsEvent {
  type: string;
  payload: {
    ticket_id: number;
    number: string;
    status: string;
    window_number: number | null;
    service_id: number;
  };
}

export default function BoardPage() {
  const [tickets, setTickets] = useState<BoardTicket[]>([]);
  const [windowsMap, setWindowsMap] = useState<Record<number, string>>({});
  const [connected, setConnected] = useState(false);
  const windowNumberToId = useRef<Record<number, number>>({});

  useEffect(() => {
    getWindows()
      .then((ws) => {
        const map: Record<number, string> = {};
        const numToId: Record<number, number> = {};
        ws.forEach((w) => {
          map[w.id] = w.name;
          numToId[w.number] = w.id;
        });
        setWindowsMap(map);
        windowNumberToId.current = numToId;
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let pollTimer: number | null = null;
    let closed = false;

    const loadTickets = () => {
      getBoardTickets()
        .then(setTickets)
        .catch(() => {});
    };

    loadTickets();

    const handleEvent = (event: WsEvent) => {
      const p = event.payload;

      if (event.type === 'ticket_called') {
        const windowId = p.window_number
          ? windowNumberToId.current[p.window_number] ?? null
          : null;
        const newTicket: BoardTicket = {
          id: p.ticket_id,
          number: p.number,
          status: p.status,
          priority: 0,
          service_id: p.service_id,
          window_id: windowId,
          created_at: new Date().toISOString(),
        };
        setTickets((prev) => {
          const without = prev.filter((t) => t.id !== p.ticket_id);
          return [newTicket, ...without].slice(0, 10);
        });
      } else if (
        event.type === 'ticket_completed' ||
        event.type === 'ticket_missed'
      ) {
        setTickets((prev) => prev.filter((t) => t.id !== p.ticket_id));
      }
    };

    const connect = () => {
      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const url = `${proto}://${window.location.host}/ws/queue`;
      ws = new WebSocket(url);

      ws.onopen = () => {
        setConnected(true);
        loadTickets();
      };

      ws.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data) as WsEvent;
          if (event.type && event.payload) {
            handleEvent(event);
          }
        } catch {
          loadTickets();
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (!closed) {
          reconnectTimer = window.setTimeout(connect, 2000);
        }
      };

      ws.onerror = () => {
        ws?.close();
      };
    };

    connect();

    pollTimer = window.setInterval(loadTickets, 30000);

    return () => {
      closed = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      if (pollTimer !== null) clearInterval(pollTimer);
      ws?.close();
    };
  }, []);

  return (
    <div style={{ padding: 32 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <h1>Табло очереди</h1>
        <span
          style={{
            width: 12,
            height: 12,
            borderRadius: '50%',
            background: connected ? '#4caf50' : '#f44336',
          }}
          title={connected ? 'WebSocket подключён' : 'Нет соединения'}
        />
      </div>

      {tickets.length === 0 ? (
        <p style={{ fontSize: 24, color: '#666' }}>Пока никого не вызвали</p>
      ) : (
        <div style={{ display: 'grid', gap: 24, marginTop: 24 }}>
          {tickets.map((t) => (
            <div
              key={t.id}
              style={{
                fontSize: 48,
                display: 'flex',
                alignItems: 'center',
                gap: 24,
              }}
            >
              <strong>{t.number}</strong>
              <span>→</span>
              <span>
                {t.window_id
                  ? windowsMap[t.window_id] ?? `Окно #${t.window_id}`
                  : '—'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
