import { api } from '../../../shared/services/api';
import type { Aviso, AvisoCreatePayload } from '../types/coordinacion.types';

export const avisosService = {
  crearAviso: async (payload: AvisoCreatePayload) => {
    const response = await api.post<Aviso>('/avisos/', payload);
    return response.data;
  },

  getActivos: async () => {
    const response = await api.get<Aviso[]>('/avisos/activos');
    return response.data;
  },

  acusarRecibo: async (avisoId: string) => {
    const response = await api.post('/avisos/ack', { aviso_id: avisoId });
    return response.data;
  },
};
