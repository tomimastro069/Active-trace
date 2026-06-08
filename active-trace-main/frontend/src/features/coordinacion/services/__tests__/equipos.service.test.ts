import { describe, it, expect, vi, beforeEach } from 'vitest';
import { equiposService } from '../equipos.service';
import { api } from '../../../../shared/services/api';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

describe('equipos.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getMisEquipos calls the correct endpoint', async () => {
    const mockData = [{ id: 'a1' }];
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockData });

    const result = await equiposService.getMisEquipos();
    expect(api.get).toHaveBeenCalledWith('/equipos/mis-equipos');
    expect(result).toEqual(mockData);
  });

  it('asignacionMasiva posts the payload', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: [] });
    const payload = { usuario_ids: ['u1'], rol_id: 'r1', desde: '2026-01-01' };

    await equiposService.asignacionMasiva(payload);
    expect(api.post).toHaveBeenCalledWith('/equipos/masiva', payload);
  });

  it('clonarEquipo posts to the clone endpoint', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: [] });
    const payload = {
      source_materia_id: 'm1', source_cohorte_id: 'c1',
      target_materia_id: 'm2', target_cohorte_id: 'c2',
      nuevo_desde: '2026-03-01',
    };

    await equiposService.clonarEquipo(payload);
    expect(api.post).toHaveBeenCalledWith('/equipos/clonar', payload);
  });

  it('modificarVigencia patches the endpoint', async () => {
    vi.mocked(api.patch).mockResolvedValueOnce({ data: [] });
    await equiposService.modificarVigencia({ materia_id: 'm1' });
    expect(api.patch).toHaveBeenCalledWith('/equipos/vigencia', { materia_id: 'm1' });
  });

  it('exportarEquipo requests a blob', async () => {
    const blob = new Blob(['csv']);
    vi.mocked(api.get).mockResolvedValueOnce({ data: blob });

    const result = await equiposService.exportarEquipo({ materia_id: 'm1' });
    expect(api.get).toHaveBeenCalledWith('/equipos/exportar', {
      params: { materia_id: 'm1' },
      responseType: 'blob',
    });
    expect(result).toBe(blob);
  });
});
