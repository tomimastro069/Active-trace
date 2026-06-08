import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { equiposService } from '../services/equipos.service';
import type { EquipoClonarPayload } from '../types/coordinacion.types';

const emptyClonar: EquipoClonarPayload = {
  source_materia_id: '',
  source_cohorte_id: '',
  target_materia_id: '',
  target_cohorte_id: '',
  nuevo_desde: '',
};

export const EquiposPage = () => {
  const queryClient = useQueryClient();
  const [clonar, setClonar] = useState<EquipoClonarPayload>(emptyClonar);
  const [feedback, setFeedback] = useState<string | null>(null);

  const { data: equipos, isLoading, isError } = useQuery({
    queryKey: ['mis-equipos'],
    queryFn: equiposService.getMisEquipos,
  });

  const clonarMutation = useMutation({
    mutationFn: () => equiposService.clonarEquipo(clonar),
    onSuccess: () => {
      setFeedback('Equipo clonado correctamente.');
      setClonar(emptyClonar);
      queryClient.invalidateQueries({ queryKey: ['mis-equipos'] });
    },
    onError: (err: unknown) => {
      const status = (err as { response?: { status?: number } })?.response?.status;
      setFeedback(status === 409 ? 'El destino ya tiene asignaciones activas.' : 'Error al clonar el equipo.');
    },
  });

  const handleExport = async () => {
    const blob = await equiposService.exportarEquipo({});
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'equipo_docente.csv';
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="p-8 space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Equipos Docentes</h1>
          <p className="text-sm text-slate-500">Gestión de asignaciones, clonado de equipos y exportación.</p>
        </div>
        <button
          onClick={handleExport}
          className="px-4 py-2 text-sm font-medium text-white bg-slate-700 rounded hover:bg-slate-800 transition-colors"
        >
          Exportar CSV
        </button>
      </header>

      {feedback && (
        <div className="rounded border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700">{feedback}</div>
      )}

      <section>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Mis Equipos</h2>
        {isLoading && <div className="text-slate-500">Cargando equipos...</div>}
        {isError && <div className="text-red-500">Error al cargar los equipos.</div>}
        {equipos && (
          <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-3 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Usuario</th>
                  <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Rol</th>
                  <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Materia</th>
                  <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Cohorte</th>
                  <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Vigencia</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {equipos.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-sm text-slate-500">
                      No tenés equipos asignados.
                    </td>
                  </tr>
                )}
                {equipos.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50">
                    <td className="py-3 pl-4 pr-3 text-sm text-gray-900">{a.usuario_id}</td>
                    <td className="px-3 py-3 text-sm text-gray-500">{a.rol_id}</td>
                    <td className="px-3 py-3 text-sm text-gray-500">{a.materia_id ?? '—'}</td>
                    <td className="px-3 py-3 text-sm text-gray-500">{a.cohorte_id ?? '—'}</td>
                    <td className="px-3 py-3 text-sm">
                      <span className="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">
                        {a.estado_vigencia}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="max-w-2xl">
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Clonar Equipo entre Períodos</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            clonarMutation.mutate();
          }}
          className="grid grid-cols-2 gap-3 rounded-lg border border-slate-200 p-4"
        >
          <input required placeholder="Materia origen" value={clonar.source_materia_id}
            onChange={(e) => setClonar({ ...clonar, source_materia_id: e.target.value })}
            className="rounded border border-slate-300 px-3 py-2 text-sm" />
          <input required placeholder="Cohorte origen" value={clonar.source_cohorte_id}
            onChange={(e) => setClonar({ ...clonar, source_cohorte_id: e.target.value })}
            className="rounded border border-slate-300 px-3 py-2 text-sm" />
          <input required placeholder="Materia destino" value={clonar.target_materia_id}
            onChange={(e) => setClonar({ ...clonar, target_materia_id: e.target.value })}
            className="rounded border border-slate-300 px-3 py-2 text-sm" />
          <input required placeholder="Cohorte destino" value={clonar.target_cohorte_id}
            onChange={(e) => setClonar({ ...clonar, target_cohorte_id: e.target.value })}
            className="rounded border border-slate-300 px-3 py-2 text-sm" />
          <input required type="date" value={clonar.nuevo_desde}
            onChange={(e) => setClonar({ ...clonar, nuevo_desde: e.target.value })}
            className="col-span-2 rounded border border-slate-300 px-3 py-2 text-sm" />
          <button
            type="submit"
            disabled={clonarMutation.isPending}
            className="col-span-2 rounded bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {clonarMutation.isPending ? 'Clonando...' : 'Clonar Equipo'}
          </button>
        </form>
      </section>
    </div>
  );
};
