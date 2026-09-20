import { coreApi } from './client';

export interface User {
  id: number;
  username: string;
  full_name: string | null;
  role: string;
}

export async function getOperators(): Promise<User[]> {
  const response = await coreApi.get<User[]>('/users/operators');
  return response.data;
}
