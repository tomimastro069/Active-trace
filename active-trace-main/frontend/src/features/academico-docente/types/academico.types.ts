export interface CommissionContextType {
  materiaId: string;
  cohorteId: string;
  umbralPct: number;
  setUmbralPct: (val: number) => void;
}

export interface AlumnoAtrasado {
  padron_id: string;
  nombre: string;
  apellido: string;
  email: string;
  tareas_faltantes: string[];
  nota_actual?: number;
  estado_general: string;
}

export interface RankingItem {
  padron_id: string;
  nombre: string;
  apellido: string;
  tareas_aprobadas: number;
  promedio_final: number;
}

export interface ConfiguracionUmbral {
  umbral_aprobacion: number;
}

export interface PreviewCalificaciones {
  actividades: string[];
  registros: any[]; // Depends on CSV structure
}

export interface MonitorItem {
  padron_id: string;
  nombre: string;
  apellido: string;
  comision_id: string;
  regional: string;
  porcentaje_cumplimiento: number;
}

export interface EntregaPendiente {
  padron_id: string;
  nombre: string;
  apellido: string;
  tarea: string;
  fecha_entrega: string;
}

