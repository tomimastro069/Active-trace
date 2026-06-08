import { api } from '../../../shared/services/api';
import type { MonitorItem, MonitorFiltros } from '../types/coordinacion.types';

export const monitorService = {
  getMonitor: async (filtros: MonitorFiltros) => {
    // Omitir parámetros vacíos para no enviar query strings inútiles.
    const params = Object.fromEntries(
      Object.entries(filtros).filter(([, value]) => value !== undefined && value !== '')
    );
    const response = await api.get<MonitorItem[]>('/analisis/monitor', { params });
    return response.data;
  },
};
