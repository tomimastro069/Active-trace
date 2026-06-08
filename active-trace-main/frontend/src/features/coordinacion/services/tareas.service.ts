import { api } from '../../../shared/services/api';
import type {
  Tarea,
  TareaCreatePayload,
  EstadoTarea,
  ComentarioTarea,
} from '../types/coordinacion.types';

export const tareasService = {
  listTareas: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get<Tarea[]>('/tareas/', { params });
    return response.data;
  },

  crearTarea: async (payload: TareaCreatePayload) => {
    const response = await api.post<Tarea>('/tareas/', payload);
    return response.data;
  },

  getTarea: async (tareaId: string) => {
    const response = await api.get<Tarea>(`/tareas/${tareaId}`);
    return response.data;
  },

  cambiarEstado: async (tareaId: string, estado: EstadoTarea) => {
    const response = await api.patch<Tarea>(`/tareas/${tareaId}`, { estado });
    return response.data;
  },

  getComentarios: async (tareaId: string) => {
    const response = await api.get<ComentarioTarea[]>(`/tareas/${tareaId}/comentarios`);
    return response.data;
  },

  agregarComentario: async (tareaId: string, texto: string) => {
    const response = await api.post<ComentarioTarea>(`/tareas/${tareaId}/comentarios`, { texto });
    return response.data;
  },
};
