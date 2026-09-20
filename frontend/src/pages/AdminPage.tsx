import { useEffect, useState } from 'react';
import {
  login,
  saveSession,
  getToken,
  getRole,
  clearSession,
} from '../api/auth';
import { getOperators, type User } from '../api/users';
import { getServices, type Service } from '../api/services';
import { getWindows, createWindow, type Window } from '../api/windows';

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(getToken());
  const [role, setRole] = useState<string | null>(getRole());

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState<string | null>(null);

  const [operators, setOperators] = useState<User[]>([]);
  const [windows, setWindows] = useState<Window[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [newNumber, setNewNumber] = useState<string>('');
  const [newName, setNewName] = useState<string>('');
  const [selectedServiceIds, setSelectedServiceIds] = useState<number[]>([]);
  const [creating, setCreating] = useState(false);

  function loadAll() {
    setLoading(true);
    setError(null);
    Promise.all([getOperators(), getWindows(), getServices()])
      .then(([ops, wins, svcs]) => {
        setOperators(ops);
        setWindows(wins);
        setServices(svcs);
      })
      .catch((e: any) => {
        const status = e?.response?.status;
        if (status === 401 || status === 403) {
          setError('Нужны права администратора. Войдите заново.');
          clearSession();
          setToken(null);
          setRole(null);
        } else {
          setError('Не удалось загрузить данные');
        }
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (token && role === 'ADMIN') {
      loadAll();
    }
  }, [token, role]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginError(null);
    try {
      const data = await login(username, password);
      if (data.role !== 'ADMIN') {
        setLoginError('Этот аккаунт не является администратором');
        return;
      }
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
    setOperators([]);
    setWindows([]);
    setServices([]);
  }

  function toggleService(id: number) {
    setSelectedServiceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newNumber || !newName) return;
    setCreating(true);
    setError(null);
    try {
      await createWindow({
        number: Number(newNumber),
        name: newName,
        service_ids: selectedServiceIds,
      });
      setNewNumber('');
      setNewName('');
      setSelectedServiceIds([]);
      loadAll();
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? 'Ошибка создания окна';
      setError(msg);
    } finally {
      setCreating(false);
    }
  }

  if (!token || role !== 'ADMIN') {
    return (
      <div style={{ padding: 32, maxWidth: 400, margin: '0 auto' }}>
        <h1>Вход администратора</h1>
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

  if (loading) return <div style={{ padding: 32 }}>Загрузка…</div>;

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h1>Администрирование</h1>
        <div>
          <span style={{ marginRight: 12, color: '#666' }}>{role}</span>
          <button onClick={handleLogout} style={{ padding: '8px 16px' }}>
            Выйти
          </button>
        </div>
      </div>

      {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}

      <h2 style={{ marginTop: 32 }}>Окна</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ccc', textAlign: 'left' }}>
            <th style={{ padding: 8 }}>№</th>
            <th style={{ padding: 8 }}>Название</th>
            <th style={{ padding: 8 }}>Услуги</th>
            <th style={{ padding: 8 }}>Активно</th>
          </tr>
        </thead>
        <tbody>
          {windows.map((w) => (
            <tr key={w.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{w.number}</td>
              <td style={{ padding: 8 }}>{w.name}</td>
              <td style={{ padding: 8 }}>
                {w.services.map((s) => s.name).join(', ') || '—'}
              </td>
              <td style={{ padding: 8 }}>{w.is_active ? 'да' : 'нет'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: 32 }}>Создать окно</h2>
      <form
        onSubmit={handleCreate}
        style={{ display: 'grid', gap: 12, maxWidth: 500 }}
      >
        <input
          type="number"
          placeholder="Номер окна"
          value={newNumber}
          onChange={(e) => setNewNumber(e.target.value)}
          style={{ padding: 8, fontSize: 16 }}
        />
        <input
          placeholder="Название (например, Окно 3)"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          style={{ padding: 8, fontSize: 16 }}
        />
        <div>
          <div style={{ marginBottom: 8 }}>Услуги:</div>
          {services.map((s) => (
            <label key={s.id} style={{ display: 'block', padding: '4px 0' }}>
              <input
                type="checkbox"
                checked={selectedServiceIds.includes(s.id)}
                onChange={() => toggleService(s.id)}
                style={{ marginRight: 8 }}
              />
              {s.name} ({s.prefix})
            </label>
          ))}
        </div>
        <button
          type="submit"
          disabled={creating}
          style={{ padding: 12, fontSize: 16, cursor: 'pointer' }}
        >
          {creating ? 'Создание…' : 'Создать окно'}
        </button>
      </form>

      <h2 style={{ marginTop: 32 }}>Операторы</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ccc', textAlign: 'left' }}>
            <th style={{ padding: 8 }}>Логин</th>
            <th style={{ padding: 8 }}>Имя</th>
            <th style={{ padding: 8 }}>Роль</th>
          </tr>
        </thead>
        <tbody>
          {operators.map((u) => (
            <tr key={u.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{u.username}</td>
              <td style={{ padding: 8 }}>{u.full_name ?? '—'}</td>
              <td style={{ padding: 8 }}>{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
