import { describe, it, expect, vi, beforeEach } from 'vitest';
import { monitorService } from '../monitor.service';
import { api } from '../../../../shared/services/api';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('monitor.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getMonitor sends required params and omits empty ones', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [] });

    await monitorService.getMonitor({
      materia_id: 'm1',
      cohorte_id: 'c1',
      regional: '',
      search: 'juan',
    });

    expect(api.get).toHaveBeenCalledWith('/analisis/monitor', {
      params: { materia_id: 'm1', cohorte_id: 'c1', search: 'juan' },
    });
  });
});
