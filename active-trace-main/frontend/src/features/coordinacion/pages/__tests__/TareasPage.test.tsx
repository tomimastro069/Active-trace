// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TareasPage } from '../TareasPage';
import { tareasService } from '../../services/tareas.service';
import type { Tarea } from '../../types/coordinacion.types';

vi.mock('../../services/tareas.service', () => ({
  tareasService: {
    listTareas: vi.fn(),
    crearTarea: vi.fn(),
    cambiarEstado: vi.fn(),
    getComentarios: vi.fn(),
    agregarComentario: vi.fn(),
  },
}));

const baseTarea: Tarea = {
  id: 't1',
  descripcion: 'Revisar padrón',
  asignado_a: 'u2',
  asignado_por: 'u1',
  estado: 'Pendiente',
  created_at: '2026-06-01T00:00:00Z',
  updated_at: '2026-06-01T00:00:00Z',
};

const renderPage = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TareasPage />
    </QueryClientProvider>
  );
};

describe('TareasPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it('renders tasks grouped by workflow state', async () => {
    vi.mocked(tareasService.listTareas).mockResolvedValueOnce([baseTarea]);
    renderPage();

    expect(await screen.findByText('Revisar padrón')).toBeInTheDocument();
    // The four workflow column headings are present.
    expect(screen.getByRole('heading', { name: 'Pendiente' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'En progreso' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Resuelta' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Cancelada' })).toBeInTheDocument();
  });

  it('creates a task through the form', async () => {
    vi.mocked(tareasService.listTareas).mockResolvedValue([]);
    vi.mocked(tareasService.crearTarea).mockResolvedValueOnce(baseTarea);
    renderPage();

    fireEvent.change(screen.getByPlaceholderText('Descripción de la tarea'), {
      target: { value: 'Nueva tarea' },
    });
    fireEvent.change(screen.getByPlaceholderText('Asignar a (usuario ID)'), {
      target: { value: 'u2' },
    });
    fireEvent.click(screen.getByText('Crear / Delegar'));

    await waitFor(() =>
      expect(tareasService.crearTarea).toHaveBeenCalledWith({
        descripcion: 'Nueva tarea',
        asignado_a: 'u2',
      })
    );
  });

  it('transitions a task to a new state', async () => {
    vi.mocked(tareasService.listTareas).mockResolvedValue([baseTarea]);
    vi.mocked(tareasService.cambiarEstado).mockResolvedValueOnce({ ...baseTarea, estado: 'En progreso' });
    renderPage();

    const select = await screen.findByDisplayValue('Pendiente');
    fireEvent.change(select, { target: { value: 'En progreso' } });

    await waitFor(() =>
      expect(tareasService.cambiarEstado).toHaveBeenCalledWith('t1', 'En progreso')
    );
  });
});
