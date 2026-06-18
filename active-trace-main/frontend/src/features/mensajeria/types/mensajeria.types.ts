export interface Message {
  id: string;
  thread_id: string;
  remitente_id: string;
  remitente_nombre?: string | null;
  contenido: string;
  created_at: string;
}

export interface Thread {
  id: string;
  tenant_id: string;
  asunto: string;
  creador_id: string;
  is_closed: boolean;
  created_at: string;
  updated_at: string;
  miembros: string[];
  mensajes?: Message[] | null;
}

export interface ThreadCreatePayload {
  asunto: string;
  destinatario_id: string;
  mensaje: string;
}
