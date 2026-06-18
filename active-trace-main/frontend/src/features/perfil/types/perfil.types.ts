export interface Perfil {
  id: string;
  email: string;
  nombre: string | null;
  apellidos: string | null;
  estado: string;
  dni?: string | null;
  cuil?: string | null;
  cbu?: string | null;
  alias_cbu?: string | null;
  banco?: string | null;
  regional?: string | null;
  legajo?: string | null;
  legajo_profesional?: string | null;
  modalidad_cobro?: string | null;
}

export interface PerfilUpdatePayload {
  nombre?: string | null;
  apellidos?: string | null;
  dni?: string | null;
  cbu?: string | null;
  alias_cbu?: string | null;
  banco?: string | null;
  regional?: string | null;
  legajo_profesional?: string | null;
  modalidad_cobro?: string | null;
  email?: string | null;
}
