import axios from 'axios';

const CORE_URL =
  import.meta.env.VITE_API_CORE_URL ?? 'http://localhost:8000/api/v1';

export const coreApi = axios.create({
  baseURL: CORE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
