import { api } from '../../../shared/services/api';
import type {
  Asignacion,
  AsignacionMasivaPayload,
  EquipoClonarPayload,
  AsignacionVigenciaPayload,
} from '../types/coordinacion.types';

export const equiposService = {
  getMisEquipos: async () => {
    const response = await api.get<Asignacion[]>('/equipos/mis-equipos');
    return response.data;
  },

  asignacionMasiva: async (payload: AsignacionMasivaPayload) => {
    const response = await api.post<Asignacion[]>('/equipos/masiva', payload);
    return response.data;
  },

  clonarEquipo: async (payload: EquipoClonarPayload) => {
    const response = await api.post<Asignacion[]>('/equipos/clonar', payload);
    return response.data;
  },

  modificarVigencia: async (payload: AsignacionVigenciaPayload) => {
    const response = await api.patch<Asignacion[]>('/equipos/vigencia', payload);
    return response.data;
  },

  exportarEquipo: async (params: { materia_id?: string; carrera_id?: string; cohorte_id?: string }) => {
    const response = await api.get('/equipos/exportar', { params, responseType: 'blob' });
    return response.data as Blob;
  },
};
