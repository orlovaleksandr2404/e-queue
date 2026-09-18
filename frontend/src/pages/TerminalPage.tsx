import { useEffect, useState } from 'react';
import { getServices, createTicket, type Service, type Ticket } from '../api/services';

export default function TerminalPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ticket, setTicket] = useState<Ticket | null>(null);

  useEffect(() => {
    getServices()
      .then(setServices)
      .catch(() => setError('Не удалось загрузить услуги'))
      .finally(() => setLoading(false));
  }, []);

  async function handleGetTicket(serviceId: number) {
    try {
      const t = await createTicket(serviceId);
      setTicket(t);
    } catch {
      setError('Не удалось получить талон');
    }
  }

  if (loading) {
    return <div style={{ padding: 32 }}>Загрузка…</div>;
  }

  if (error) {
    return <div style={{ padding: 32, color: 'red' }}>{error}</div>;
  }

  if (ticket) {
    return (
      <div style={{ padding: 64, textAlign: 'center' }}>
        <h1>Ваш талон</h1>
        <div style={{ fontSize: 120, fontWeight: 'bold', margin: '32px 0' }}>
          {ticket.number}
        </div>
        <p style={{ fontSize: 20, color: '#666' }}>
          Ожидайте вызова на табло
        </p>
        <button
          onClick={() => setTicket(null)}
          style={{ marginTop: 32, padding: '12px 24px', fontSize: 16 }}
        >
          Вернуться
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: 32 }}>
      <h1>Выберите услугу</h1>
      <div style={{ display: 'grid', gap: 16, marginTop: 24 }}>
        {services.map((s) => (
          <button
            key={s.id}
            onClick={() => handleGetTicket(s.id)}
            style={{
              padding: 24,
              fontSize: 20,
              textAlign: 'left',
              cursor: 'pointer',
            }}
          >
            <strong>{s.name}</strong>
            <span style={{ color: '#666', marginLeft: 12 }}>
              ~{s.avg_duration_minutes} мин
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
