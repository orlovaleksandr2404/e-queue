import { coreApi } from './client';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: number;
}

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const response = await coreApi.post<LoginResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
}

export function saveSession(data: LoginResponse) {
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('role', data.role);
  localStorage.setItem('user_id', String(data.user_id));
}

export function getToken(): string | null {
  return localStorage.getItem('access_token');
}

export function getRole(): string | null {
  return localStorage.getItem('role');
}

export function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('role');
  localStorage.removeItem('user_id');
}
