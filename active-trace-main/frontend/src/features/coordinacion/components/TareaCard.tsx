import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tareasService } from '../services/tareas.service';
import { ESTADOS_TAREA, type EstadoTarea, type Tarea } from '../types/coordinacion.types';

interface TareaCardProps {
  tarea: Tarea;
  onSelect: (tarea: Tarea) => void;
}

export const TareaCard = ({ tarea, onSelect }: TareaCardProps) => {
  const queryClient = useQueryClient();

  const estadoMutation = useMutation({
    mutationFn: (estado: EstadoTarea) => tareasService.cambiarEstado(tarea.id, estado),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tareas'] }),
  });

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <button onClick={() => onSelect(tarea)} className="block w-full text-left">
        <p className="text-sm font-medium text-slate-800 line-clamp-3">{tarea.descripcion}</p>
        <p className="mt-1 text-xs text-slate-400">Asignado a: {tarea.asignado_a}</p>
      </button>
      <select
        value={tarea.estado}
        onChange={(e) => estadoMutation.mutate(e.target.value as EstadoTarea)}
        disabled={estadoMutation.isPending}
        className="mt-2 w-full rounded border border-slate-300 px-2 py-1 text-xs"
      >
        {ESTADOS_TAREA.map((estado) => (
          <option key={estado} value={estado}>{estado}</option>
        ))}
      </select>
    </div>
  );
};
