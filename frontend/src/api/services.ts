import { coreApi } from './client';

export interface Service {
  id: number;
  name: string;
  prefix: string;
  avg_duration_minutes: number;
}

export interface Ticket {
  id: number;
  number: string;
  status: string;
  service_id: number;
  created_at: string;
}

export async function getServices(): Promise<Service[]> {
  const response = await coreApi.get<Service[]>('/services');
  return response.data;
}

export async function createTicket(serviceId: number): Promise<Ticket> {
  const response = await coreApi.post<Ticket>('/tickets', {
    service_id: serviceId,
  });
  return response.data;
}

export async function deleteService(serviceId: number): Promise<void> {
  await coreApi.delete(`/services/${serviceId}`);
}
