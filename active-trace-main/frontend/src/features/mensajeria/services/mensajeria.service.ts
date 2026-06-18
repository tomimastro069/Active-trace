import { api } from '../../../shared/services/api';
import type { Thread, Message, ThreadCreatePayload } from '../types/mensajeria.types';

export const mensajeriaService = {
  getThreads: async () => {
    const response = await api.get<Thread[]>('/threads');
    return response.data;
  },

  getThread: async (threadId: string) => {
    const response = await api.get<Thread>(`/thread/${threadId}`);
    return response.data;
  },

  crearThread: async (payload: ThreadCreatePayload) => {
    const response = await api.post<Thread>('/threads', payload);
    return response.data;
  },

  responder: async (threadId: string, contenido: string) => {
    const response = await api.post<Message>(`/thread/${threadId}/reply`, { contenido });
    return response.data;
  },
};
