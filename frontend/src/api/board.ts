import { coreApi } from './client';

export interface BoardTicket {
  id: number;
  number: string;
  status: string;
  priority: number;
  service_id: number;
  window_id: number | null;
  created_at: string;
}

export async function getBoardTickets(): Promise<BoardTicket[]> {
  const response = await coreApi.get<BoardTicket[]>('/tickets/board');
  return response.data;
}
