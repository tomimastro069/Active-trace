import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tareasService } from '../services/tareas.service';
import type { Tarea } from '../types/coordinacion.types';

interface TareaDetalleProps {
  tarea: Tarea;
  onClose: () => void;
}

export const TareaDetalle = ({ tarea, onClose }: TareaDetalleProps) => {
  const queryClient = useQueryClient();
  const [texto, setTexto] = useState('');

  const { data: comentarios, isLoading } = useQuery({
    queryKey: ['comentarios', tarea.id],
    queryFn: () => tareasService.getComentarios(tarea.id),
  });

  const comentarMutation = useMutation({
    mutationFn: () => tareasService.agregarComentario(tarea.id, texto),
    onSuccess: () => {
      setTexto('');
      queryClient.invalidateQueries({ queryKey: ['comentarios', tarea.id] });
    },
  });

  return (
    <aside className="flex h-full flex-col rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <h3 className="text-base font-semibold text-slate-800">Detalle de Tarea</h3>
        <button onClick={onClose} className="text-sm text-slate-400 hover:text-slate-600">✕</button>
      </div>
      <p className="mt-2 text-sm text-slate-700">{tarea.descripcion}</p>
      <p className="mt-1 text-xs text-slate-400">Estado: {tarea.estado}</p>

      <h4 className="mt-4 text-sm font-semibold text-slate-700">Comentarios</h4>
      <div className="mt-2 flex-1 space-y-2 overflow-y-auto">
        {isLoading && <p className="text-xs text-slate-400">Cargando comentarios...</p>}
        {comentarios?.length === 0 && <p className="text-xs text-slate-400">Sin comentarios.</p>}
        {comentarios?.map((c) => (
          <div key={c.id} className="rounded bg-slate-50 px-3 py-2 text-sm text-slate-700">
            {c.texto}
            <p className="mt-1 text-xs text-slate-400">{c.autor_id}</p>
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          comentarMutation.mutate();
        }}
        className="mt-3 flex gap-2"
      >
        <input
          required
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escribir comentario..."
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={comentarMutation.isPending}
          className="rounded bg-slate-700 px-3 py-2 text-sm text-white hover:bg-slate-800 disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </aside>
  );
};
