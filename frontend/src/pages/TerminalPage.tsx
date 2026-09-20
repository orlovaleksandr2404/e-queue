import { useEffect, useState } from 'react';
import { getServices, createTicket, type Service, type Ticket } from '../api/services';
import { getWaitTime, type WaitTime } from '../api/queue';

export default function TerminalPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [waitTime, setWaitTime] = useState<WaitTime | null>(null);

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

      getWaitTime(t.id)
        .then(setWaitTime)
        .catch(() => setWaitTime(null));
    } catch {
      setError('Не удалось получить талон');
    }
  }

  function reset() {
    setTicket(null);
    setWaitTime(null);
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
        <div style={{ fontSize: 140, fontWeight: 'bold', margin: '32px 0' }}>
          {ticket.number}
        </div>

        {waitTime && (
          <div
            style={{
              fontSize: 24,
              color: '#555',
              marginTop: 16,
              lineHeight: 1.6,
            }}
          >
            <div>
              Перед вами:{' '}
              <strong>{waitTime.position - 1}</strong>{' '}
              {getPersonWord(waitTime.position - 1)}
            </div>
            <div>
              Примерное время ожидания:{' '}
              <strong>~{waitTime.eta_minutes} мин</strong>
            </div>
          </div>
        )}

        <p style={{ fontSize: 20, color: '#666', marginTop: 24 }}>
          Ожидайте вызова на табло
        </p>
        <button
          onClick={reset}
          style={{
            marginTop: 32,
            padding: '12px 24px',
            fontSize: 16,
            cursor: 'pointer',
          }}
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

function getPersonWord(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return 'человек';
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return 'человека';
  return 'человек';
}
