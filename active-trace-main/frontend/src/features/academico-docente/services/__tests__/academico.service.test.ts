import { describe, it, expect, vi, beforeEach } from 'vitest';
import { academicoService } from '../academico.service';
import { api } from '../../../../shared/services/api';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  }
}));

describe('academico.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getUmbral should call the correct endpoint', async () => {
    const mockData = { umbral_aprobacion: 70 };
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockData });

    const result = await academicoService.getUmbral('M1', 'C1');
    expect(api.get).toHaveBeenCalledWith('/calificaciones/comision/M1/C1/umbral');
    expect(result).toEqual(mockData);
  });

  it('setUmbral should call the correct endpoint', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { success: true } });

    await academicoService.setUmbral('M1', 'C1', 65);
    expect(api.post).toHaveBeenCalledWith('/calificaciones/comision/M1/C1/umbral', { umbral_aprobacion: 65 });
  });

  it('getRanking should call the correct endpoint', async () => {
    const mockData = [{ padron_id: '123' }];
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockData });

    const result = await academicoService.getRanking('M1', 'C1');
    expect(api.get).toHaveBeenCalledWith('/analisis/ranking/M1/C1');
    expect(result).toEqual(mockData);
  });

  it('getMonitor should call the correct endpoint with params', async () => {
    const mockData = [{ padron_id: '123' }];
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockData });

    const result = await academicoService.getMonitor({ search: 'juan' });
    expect(api.get).toHaveBeenCalledWith('/analisis/monitor', { params: { search: 'juan' } });
    expect(result).toEqual(mockData);
  });

  it('detectarTrabajosSinCorregir should call the correct endpoint with FormData', async () => {
    const mockData = [{ padron_id: '123', nombre: 'Juan', apellido: 'Perez', tarea: 'T1', fecha_entrega: '2026-06-08' }];
    vi.mocked(api.post).mockResolvedValueOnce({ data: mockData });

    const mockFile = new File(['csv data'], 'report.csv', { type: 'text/csv' });
    const result = await academicoService.detectarTrabajosSinCorregir('M1', 'C1', mockFile);
    
    expect(api.post).toHaveBeenCalledWith(
      '/analisis/sin-corregir/M1/C1',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    expect(result).toEqual(mockData);
  });
});
