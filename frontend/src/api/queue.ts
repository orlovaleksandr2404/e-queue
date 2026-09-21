import axios from 'axios';

const QUEUE_URL = import.meta.env.VITE_API_QUEUE_URL ?? '/api/queue/v1';

export const queueApi = axios.create({
  baseURL: QUEUE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export interface WaitTime {
  ticket_id: number;
  number: string;
  service_name: string;
  position: number;
  eta_minutes: number;
}

export async function getWaitTime(ticketId: number): Promise<WaitTime> {
  const response = await queueApi.get<WaitTime>(
    `/algorithm/tickets/${ticketId}/wait-time`,
  );
  return response.data;
}
