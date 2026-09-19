import { coreApi } from './client';

export interface Window {
  id: number;
  name: string;
  is_active: boolean;
  services: { id: number; name: string }[];
}

export interface Ticket {
  id: number;
  number: string;
  status: string;
  service_id: number;
  window_id: number | null;
  created_at: string;
}

export async function getWindows(): Promise<Window[]> {
  const response = await coreApi.get<Window[]>('/windows');
  return response.data;
}

export async function callNext(windowId: number): Promise<Ticket> {
  const response = await coreApi.post<Ticket>(
    `/windows/${windowId}/call-next`,
  );
  return response.data;
}

export async function completeTicket(ticketId: number): Promise<Ticket> {
  const response = await coreApi.post<Ticket>(
    `/windows/tickets/${ticketId}/complete`,
  );
  return response.data;
}
