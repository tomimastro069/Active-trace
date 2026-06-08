import { api } from '../../../shared/services/api';

export interface ComunicacionRequest {
  alumnos_ids: string[];
  asunto: string;
  mensaje: string;
  tipo: string;
}

export interface ComunicacionPreview {
  padron_id: string;
  email: string;
  asunto_preview: string;
  mensaje_preview: string;
}

export interface ComunicacionBatchStatus {
  batch_id: string;
  estado: string;
  total: number;
  enviados: number;
  fallidos: number;
}

export const comunicacionesService = {
  previewMensaje: async (materiaId: string, cohorteId: string, payload: ComunicacionRequest) => {
    const response = await api.post<ComunicacionPreview[]>(
      `/comunicaciones/preview/${materiaId}/${cohorteId}`, 
      payload
    );
    return response.data;
  },

  enviarLote: async (materiaId: string, cohorteId: string, payload: ComunicacionRequest) => {
    const response = await api.post<{ batch_id: string }>(
      `/comunicaciones/lote/${materiaId}/${cohorteId}`, 
      payload
    );
    return response.data;
  },

  getLoteStatus: async (batchId: string) => {
    const response = await api.get<ComunicacionBatchStatus>(`/comunicaciones/lote/${batchId}`);
    return response.data;
  }
};
