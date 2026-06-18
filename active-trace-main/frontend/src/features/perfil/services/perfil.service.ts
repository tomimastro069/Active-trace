import { api } from '../../../shared/services/api';
import type { Perfil, PerfilUpdatePayload } from '../types/perfil.types';

export const perfilService = {
  getMiPerfil: async () => {
    const response = await api.get<Perfil>('/perfil/');
    return response.data;
  },

  actualizarMiPerfil: async (payload: PerfilUpdatePayload) => {
    const response = await api.patch<Perfil>('/perfil/', payload);
    return response.data;
  },
};
