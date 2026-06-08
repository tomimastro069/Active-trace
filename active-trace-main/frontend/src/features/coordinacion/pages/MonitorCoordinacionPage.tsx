import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitorService } from '../services/monitor.service';
import type { MonitorFiltros } from '../types/coordinacion.types';

const emptyFiltros: MonitorFiltros = {
  materia_id: '',
  cohorte_id: '',
  regional: '',
  comision: '',
  search: '',
  estado_actividad: '',
};

export const MonitorCoordinacionPage = () => {
  const [form, setForm] = useState<MonitorFiltros>(emptyFiltros);
  const [filtros, setFiltros] = useState<MonitorFiltros | null>(null);

  const { data: items, isLoading, isError } = useQuery({
    queryKey: ['monitor-coordinacion', filtros],
    queryFn: () => monitorService.getMonitor(filtros as MonitorFiltros),
    enabled: !!filtros,
  });

  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">Monitor de Coordinación</h1>
        <p className="text-sm text-slate-500">Seguimiento transversal de actividades por comisión (F2.7, F2.9).</p>
      </header>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          setFiltros({ ...form });
        }}
        className="grid grid-cols-2 gap-3 rounded-lg border border-slate-200 p-4 md:grid-cols-3"
      >
        <input required placeholder="Materia ID" value={form.materia_id}
          onChange={(e) => setForm({ ...form, materia_id: e.target.value })}
          className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <input required placeholder="Cohorte ID" value={form.cohorte_id}
          onChange={(e) => setForm({ ...form, cohorte_id: e.target.value })}
          className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <input placeholder="Regional" value={form.regional}
          onChange={(e) => setForm({ ...form, regional: e.target.value })}
          className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <input placeholder="Comisión" value={form.comision}
          onChange={(e) => setForm({ ...form, comision: e.target.value })}
          className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <input placeholder="Buscar alumno" value={form.search}
          onChange={(e) => setForm({ ...form, search: e.target.value })}
          className="rounded border border-slate-300 px-3 py-2 text-sm" />
        <button
          type="submit"
          className="rounded bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Consultar
        </button>
      </form>

      {isLoading && <div className="text-slate-500">Cargando monitor...</div>}
      {isError && <div className="text-red-500">Error al cargar el monitor.</div>}

      {filtros && items && items.length === 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 py-12 text-center text-slate-500">
          No se encontraron registros para los filtros aplicados.
        </div>
      )}

      {items && items.length > 0 && (
        <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="py-3 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Padrón</th>
                <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Alumno</th>
                <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Actividad</th>
                <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Estado</th>
                <th className="px-3 py-3 text-left text-sm font-semibold text-gray-900">Nota</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {items.map((item, idx) => (
                <tr key={`${item.padron_id}-${item.actividad}-${idx}`} className="hover:bg-gray-50">
                  <td className="py-3 pl-4 pr-3 text-sm text-gray-900">{item.padron_id}</td>
                  <td className="px-3 py-3 text-sm font-medium text-gray-900">{item.apellido}, {item.nombre}</td>
                  <td className="px-3 py-3 text-sm text-gray-500">{item.actividad}</td>
                  <td className="px-3 py-3 text-sm text-gray-500">{item.estado}</td>
                  <td className="px-3 py-3 text-sm text-gray-500">{item.nota ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
