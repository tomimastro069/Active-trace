import { describe, it, expect, vi, beforeEach } from 'vitest';
import { comunicacionesService } from '../comunicaciones.service';
import { api } from '../../../../shared/services/api';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  }
}));

describe('comunicaciones.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('previewMensaje should call post to the correct endpoint', async () => {
    const mockPayload = { alumnos_ids: ['1'], asunto: 'a', mensaje: 'b', tipo: 'c' };
    const mockData = [{ padron_id: '1', email: 'test@test.com' }];
    vi.mocked(api.post).mockResolvedValueOnce({ data: mockData });

    const result = await comunicacionesService.previewMensaje('M1', 'C1', mockPayload);
    expect(api.post).toHaveBeenCalledWith('/comunicaciones/preview/M1/C1', mockPayload);
    expect(result).toEqual(mockData);
  });

  it('enviarLote should call post to the correct endpoint', async () => {
    const mockPayload = { alumnos_ids: ['1'], asunto: 'a', mensaje: 'b', tipo: 'c' };
    const mockData = { batch_id: 'batch-123' };
    vi.mocked(api.post).mockResolvedValueOnce({ data: mockData });

    const result = await comunicacionesService.enviarLote('M1', 'C1', mockPayload);
    expect(api.post).toHaveBeenCalledWith('/comunicaciones/lote/M1/C1', mockPayload);
    expect(result).toEqual(mockData);
  });

  it('getLoteStatus should call get to the correct endpoint', async () => {
    const mockData = { estado: 'ENVIANDO', enviados: 0, fallidos: 0, total: 1 };
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockData });

    const result = await comunicacionesService.getLoteStatus('batch-123');
    expect(api.get).toHaveBeenCalledWith('/comunicaciones/lote/batch-123');
    expect(result).toEqual(mockData);
  });
});
