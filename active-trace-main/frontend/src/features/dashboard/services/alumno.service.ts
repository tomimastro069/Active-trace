import { api } from '@/shared/services/api';

export interface AlumnoMateriaResponse {
  materia_id: string;
  materia_nombre: string;
  materia_codigo: string;
  cohorte_id: string;
  cohorte_nombre: string;
  porcentaje_progreso: number;
}

export interface AlumnoActividad {
  actividad: string;
  nota_numerica?: number;
  nota_textual?: string;
  aprobado: boolean;
  finalizado: boolean;
  origen: string;
}

export interface AlumnoProgresoResponse {
  materia_id: string;
  cohorte_id: string;
  actividades: AlumnoActividad[];
  porcentaje_progreso: number;
}

export const alumnoService = {
  getMisMaterias: async (): Promise<AlumnoMateriaResponse[]> => {
    const { data } = await api.get('/alumno/materias');
    return data;
  },

  getMiProgreso: async (materiaId: string): Promise<AlumnoProgresoResponse> => {
    const { data } = await api.get(`/alumno/materias/${materiaId}/progreso`);
    return data;
  }
};
