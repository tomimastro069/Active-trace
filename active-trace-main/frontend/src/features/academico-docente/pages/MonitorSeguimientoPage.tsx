import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { academicoService } from '../services/academico.service';

export const MonitorSeguimientoPage = () => {
  const [search, setSearch] = useState('');
  const [comision, setComision] = useState('');
  const [cumplimientoMax, setCumplimientoMax] = useState<number | undefined>(undefined);

  const { data: monitorItems, isLoading, isError } = useQuery({
    queryKey: ['monitor', search, comision, cumplimientoMax],
    queryFn: () => academicoService.getMonitor({ search, comision, cumplimientoMax }),
  });

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Monitor de Seguimiento Transversal</h1>
      
      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 mb-6 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-slate-700">Buscar (Nombre/Padrón)</label>
          <input 
            type="text" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="mt-1 block rounded-md border-gray-300 shadow-sm border p-2 text-sm"
            placeholder="Ej: 12345"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Comisión</label>
          <input 
            type="text" 
            value={comision}
            onChange={(e) => setComision(e.target.value)}
            className="mt-1 block rounded-md border-gray-300 shadow-sm border p-2 text-sm"
            placeholder="Todas"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Cumplimiento Máx (%)</label>
          <select 
            value={cumplimientoMax || ''}
            onChange={(e) => setCumplimientoMax(e.target.value ? Number(e.target.value) : undefined)}
            className="mt-1 block rounded-md border-gray-300 shadow-sm border p-2 text-sm w-32 bg-white"
          >
            <option value="">Cualquiera</option>
            <option value="50">&lt;= 50%</option>
            <option value="60">&lt;= 60%</option>
            <option value="70">&lt;= 70%</option>
          </select>
        </div>
      </div>

      {/* Resultados */}
      {isLoading ? (
        <div className="text-slate-500">Cargando datos del monitor...</div>
      ) : isError ? (
        <div className="text-red-500">Error al cargar datos del monitor.</div>
      ) : monitorItems && monitorItems.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Alumno</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Padrón</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comisión</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Regional</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avance</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {monitorItems.map(item => (
                <tr key={`${item.padron_id}-${item.comision_id}`} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.apellido}, {item.nombre}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.padron_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.comision_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.regional}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900 mr-2">{item.porcentaje_cumplimiento}%</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            item.porcentaje_cumplimiento < 50 ? 'bg-red-500' : 
                            item.porcentaje_cumplimiento < 70 ? 'bg-yellow-500' : 'bg-green-500'
                          }`} 
                          style={{ width: `${item.porcentaje_cumplimiento}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg border border-slate-200 text-slate-500">
          No se encontraron alumnos con los filtros seleccionados.
        </div>
      )}
    </div>
  );
};
