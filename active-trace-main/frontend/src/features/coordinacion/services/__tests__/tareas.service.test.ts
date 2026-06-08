import { describe, it, expect, vi, beforeEach } from 'vitest';
import { tareasService } from '../tareas.service';
import { api } from '../../../../shared/services/api';

vi.mock('../../../../shared/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

describe('tareas.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('listTareas calls the list endpoint with params', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [] });
    await tareasService.listTareas({ skip: 0, limit: 50 });
    expect(api.get).toHaveBeenCalledWith('/tareas/', { params: { skip: 0, limit: 50 } });
  });

  it('crearTarea posts the payload', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 't1' } });
    const payload = { descripcion: 'Revisar', asignado_a: 'u2' };
    await tareasService.crearTarea(payload);
    expect(api.post).toHaveBeenCalledWith('/tareas/', payload);
  });

  it('cambiarEstado patches the task with the new estado', async () => {
    vi.mocked(api.patch).mockResolvedValueOnce({ data: { id: 't1', estado: 'En progreso' } });
    await tareasService.cambiarEstado('t1', 'En progreso');
    expect(api.patch).toHaveBeenCalledWith('/tareas/t1', { estado: 'En progreso' });
  });

  it('getComentarios fetches the thread', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: [] });
    await tareasService.getComentarios('t1');
    expect(api.get).toHaveBeenCalledWith('/tareas/t1/comentarios');
  });

  it('agregarComentario posts the texto', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 'c1' } });
    await tareasService.agregarComentario('t1', 'hola');
    expect(api.post).toHaveBeenCalledWith('/tareas/t1/comentarios', { texto: 'hola' });
  });
});
