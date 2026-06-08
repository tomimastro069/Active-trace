import { api } from '../../../shared/services/api';
import type { AlumnoAtrasado, RankingItem, ConfiguracionUmbral, MonitorItem, EntregaPendiente } from '../types/academico.types';

export const academicoService = {
  // Configuración de Umbral
  getUmbral: async (materiaId: string, cohorteId: string) => {
    const response = await api.get<ConfiguracionUmbral>(`/calificaciones/comision/${materiaId}/${cohorteId}/umbral`);
    return response.data;
  },
  
  setUmbral: async (materiaId: string, cohorteId: string, umbral: number) => {
    const response = await api.post(`/calificaciones/comision/${materiaId}/${cohorteId}/umbral`, { umbral_aprobacion: umbral });
    return response.data;
  },

  // Importación de notas
  previewCalificaciones: async (materiaId: string, cohorteId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/calificaciones/comision/${materiaId}/${cohorteId}/preview`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  importarCalificaciones: async (materiaId: string, cohorteId: string, actividades: string[], file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('actividades', JSON.stringify(actividades));
    const response = await api.post(`/calificaciones/comision/${materiaId}/${cohorteId}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  vaciarCalificaciones: async (materiaId: string, cohorteId: string) => {
    const response = await api.delete(`/calificaciones/comision/${materiaId}/${cohorteId}`);
    return response.data;
  },

  // Análisis y Reportes
  getAtrasados: async (materiaId: string, cohorteId: string) => {
    const response = await api.get<AlumnoAtrasado[]>(`/analisis/atrasados/${materiaId}/${cohorteId}`);
    return response.data;
  },

  getRanking: async (materiaId: string, cohorteId: string) => {
    const response = await api.get<RankingItem[]>(`/analisis/ranking/${materiaId}/${cohorteId}`);
    return response.data;
  },

  getMonitor: async (params?: { search?: string; comision?: string; cumplimientoMax?: number }) => {
    const response = await api.get<MonitorItem[]>('/analisis/monitor', { params });
    return response.data;
  },

  detectarTrabajosSinCorregir: async (materiaId: string, cohorteId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<EntregaPendiente[]>(`/analisis/sin-corregir/${materiaId}/${cohorteId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};
