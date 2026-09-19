import { useEffect, useState } from 'react';
import {
  login,
  saveSession,
  getToken,
  getRole,
  clearSession,
} from '../api/auth';
import {
  getWindows,
  callNext,
  completeTicket,
  type Window,
  type Ticket,
} from '../api/windows';

export default function OperatorPage() {
  const [token, setToken] = useState<string | null>(getToken());
  const [role, setRole] = useState<string | null>(getRole());

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState<string | null>(null);

  const [windows, setWindows] = useState<Window[]>([]);
  const [selectedWindowId, setSelectedWindowId] = useState<number | null>(null);
  const [currentTicket, setCurrentTicket] = useState<Ticket | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getWindows()
      .then((ws) => {
        setWindows(ws);
        if (ws.length > 0 && selectedWindowId === null) {
          setSelectedWindowId(ws[0].id);
        }
      })
      .catch(() => setActionError('Не удалось загрузить окна'));
  }, [token]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginError(null);
    try {
      const data = await login(username, password);
      saveSession(data);
      setToken(data.access_token);
      setRole(data.role);
    } catch {
      setLoginError('Неверный логин или пароль');
    }
  }

  function handleLogout() {
    clearSession();
    setToken(null);
    setRole(null);
    setCurrentTicket(null);
    setWindows([]);
    setSelectedWindowId(null);
  }

  async function handleCallNext() {
    if (!selectedWindowId) return;
    setActionError(null);
    try {
      const t = await callNext(selectedWindowId);
      setCurrentTicket(t);
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? 'Ошибка вызова';
      setActionError(msg);
    }
  }

  async function handleComplete() {
    if (!currentTicket) return;
    setActionError(null);
    try {
      await completeTicket(currentTicket.id);
      setCurrentTicket(null);
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? 'Ошибка завершения';
      setActionError(msg);
    }
  }

  if (!token) {
    return (
      <div style={{ padding: 32, maxWidth: 400, margin: '0 auto' }}>
        <h1>Вход оператора</h1>
        <form onSubmit={handleLogin} style={{ display: 'grid', gap: 12 }}>
          <input
            placeholder="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: 12, fontSize: 16 }}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: 12, fontSize: 16 }}
          />
          <button
            type="submit"
            style={{ padding: 12, fontSize: 16, cursor: 'pointer' }}
          >
            Войти
          </button>
          {loginError && <div style={{ color: 'red' }}>{loginError}</div>}
        </form>
      </div>
    );
  }

  return (
    <div style={{ padding: 32 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h1>Кабинет оператора</h1>
        <div>
          <span style={{ marginRight: 12, color: '#666' }}>
            {role}
          </span>
          <button onClick={handleLogout} style={{ padding: '8px 16px' }}>
            Выйти
          </button>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <label style={{ marginRight: 8 }}>Рабочее окно:</label>
        <select
          value={selectedWindowId ?? ''}
          onChange={(e) => setSelectedWindowId(Number(e.target.value))}
          style={{ padding: 8, fontSize: 16 }}
        >
          {windows.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name} ({w.services.map((s) => s.name).join(', ') || 'нет услуг'})
            </option>
          ))}
        </select>
      </div>

      {actionError && (
        <div style={{ color: 'red', marginTop: 16 }}>{actionError}</div>
      )}

      {currentTicket ? (
        <div style={{ marginTop: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 20, color: '#666' }}>Вызван клиент:</div>
          <div
            style={{
              fontSize: 120,
              fontWeight: 'bold',
              margin: '16px 0',
            }}
          >
            {currentTicket.number}
          </div>
          <button
            onClick={handleComplete}
            style={{ padding: '16px 32px', fontSize: 18, cursor: 'pointer' }}
          >
            Завершить приём
          </button>
        </div>
      ) : (
        <div style={{ marginTop: 32 }}>
          <button
            onClick={handleCallNext}
            disabled={!selectedWindowId}
            style={{
              padding: '24px 48px',
              fontSize: 24,
              cursor: selectedWindowId ? 'pointer' : 'not-allowed',
            }}
          >
            Вызвать следующего
          </button>
        </div>
      )}
    </div>
  );
}
