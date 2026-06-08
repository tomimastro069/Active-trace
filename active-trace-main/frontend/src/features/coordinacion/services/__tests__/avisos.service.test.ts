import { describe, it, expect, vi, beforeEach } from 'vitest';
import { avisosService } from '../avisos.service';
import { api } from '../../../../shared/services/api';
import type { AvisoCreatePayload } from '../../types/coordinacion.types';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('avisos.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('crearAviso posts to the trailing-slash endpoint', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 'av1' } });
    const payload: AvisoCreatePayload = {
      alcance: 'Global', severidad: 'info', titulo: 'T', cuerpo: 'B',
      inicio_en: '2026-06-01T00:00', fin_en: '2026-06-30T00:00',
    };

    const result = await avisosService.crearAviso(payload);
    expect(api.post).toHaveBeenCalledWith('/avisos/', payload);
    expect(result).toEqual({ id: 'av1' });
  });

  it('getActivos calls the active endpoint', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [] });
    await avisosService.getActivos();
    expect(api.get).toHaveBeenCalledWith('/avisos/activos');
  });

  it('acusarRecibo posts the aviso_id', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { status: 'ok' } });
    await avisosService.acusarRecibo('av1');
    expect(api.post).toHaveBeenCalledWith('/avisos/ack', { aviso_id: 'av1' });
  });
});
