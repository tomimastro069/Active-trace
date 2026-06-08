import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tareasService } from '../services/tareas.service';
import { TareaCard } from '../components/TareaCard';
import { TareaDetalle } from '../components/TareaDetalle';
import { ESTADOS_TAREA, type Tarea } from '../types/coordinacion.types';

export const TareasPage = () => {
  const queryClient = useQueryClient();
  const [seleccionada, setSeleccionada] = useState<Tarea | null>(null);
  const [descripcion, setDescripcion] = useState('');
  const [asignadoA, setAsignadoA] = useState('');

  const { data: tareas, isLoading, isError } = useQuery({
    queryKey: ['tareas'],
    queryFn: () => tareasService.listTareas(),
  });

  const crearMutation = useMutation({
    mutationFn: () => tareasService.crearTarea({ descripcion, asignado_a: asignadoA }),
    onSuccess: () => {
      setDescripcion('');
      setAsignadoA('');
      queryClient.invalidateQueries({ queryKey: ['tareas'] });
    },
  });

  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">Tareas Internas</h1>
        <p className="text-sm text-slate-500">Flujo de trabajo: asignar, delegar y dar seguimiento.</p>
      </header>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          crearMutation.mutate();
        }}
        className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 p-4"
      >
        <input required placeholder="Descripción de la tarea" value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          className="flex-1 min-w-[240px] rounded border border-slate-300 px-3 py-2 text-sm" />
        <input required placeholder="Asignar a (usuario ID)" value={asignadoA}
          onChange={(e) => setAsignadoA(e.target.value)}
          className="min-w-[200px] rounded border border-slate-300 px-3 py-2 text-sm" />
        <button
          type="submit"
          disabled={crearMutation.isPending}
          className="rounded bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {crearMutation.isPending ? 'Creando...' : 'Crear / Delegar'}
        </button>
      </form>

      {isLoading && <div className="text-slate-500">Cargando tareas...</div>}
      {isError && <div className="text-red-500">Error al cargar las tareas.</div>}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="lg:col-span-3 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {ESTADOS_TAREA.map((estado) => (
            <div key={estado} className="space-y-3">
              <h2 className="text-sm font-semibold uppercase text-slate-500">{estado}</h2>
              {tareas
                ?.filter((t) => t.estado === estado)
                .map((t) => (
                  <TareaCard key={t.id} tarea={t} onSelect={setSeleccionada} />
                ))}
            </div>
          ))}
        </div>
        {seleccionada && (
          <div className="lg:col-span-1">
            <TareaDetalle tarea={seleccionada} onClose={() => setSeleccionada(null)} />
          </div>
        )}
      </div>
    </div>
  );
};
