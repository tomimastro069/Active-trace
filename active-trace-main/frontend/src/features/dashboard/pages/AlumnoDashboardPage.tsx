import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { alumnoService } from '../services/alumno.service';

export const AlumnoDashboardPage: React.FC = () => {
  const [selectedMateriaId, setSelectedMateriaId] = useState<string | null>(null);

  const { data: materias, isLoading: loadingMaterias } = useQuery({
    queryKey: ['alumno-materias'],
    queryFn: () => alumnoService.getMisMaterias()
  });

  const { data: progreso, isLoading: loadingProgreso } = useQuery({
    queryKey: ['alumno-progreso', selectedMateriaId],
    queryFn: () => alumnoService.getMiProgreso(selectedMateriaId!),
    enabled: !!selectedMateriaId
  });

  if (loadingMaterias) {
    return <div className="p-8 text-gray-500 animate-pulse">Cargando tus materias...</div>;
  }

  if (!materias || materias.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-200 mt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">No hay materias activas</h3>
        <p className="text-gray-500">No estás inscripto en ninguna materia actualmente o el padrón aún no ha sido cargado por tu docente.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {materias.map((materia) => (
          <div
            key={materia.materia_id}
            onClick={() => setSelectedMateriaId(materia.materia_id)}
            className={`cursor-pointer bg-white rounded-xl shadow-sm border p-6 transition-all hover:shadow-md hover:border-blue-200 ${
              selectedMateriaId === materia.materia_id ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50/10' : 'border-gray-100'
            }`}
          >
            <h3 className="font-semibold text-lg text-gray-900 line-clamp-1">{materia.materia_nombre}</h3>
            <p className="text-sm text-gray-500 mt-1">{materia.materia_codigo} • {materia.cohorte_nombre}</p>
            
            <div className="mt-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 font-medium">Progreso general</span>
                <span className="text-blue-700 font-semibold">{Math.round(materia.porcentaje_progreso)}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-1000 ease-out" 
                  style={{ width: `${Math.round(materia.porcentaje_progreso)}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detalle de materia */}
      {selectedMateriaId && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mt-8 animate-in slide-in-from-bottom-4 duration-500">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Detalle de Actividades</h2>
            <button 
              onClick={() => setSelectedMateriaId(null)}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Cerrar detalle
            </button>
          </div>
          
          {loadingProgreso ? (
            <div className="text-gray-500 animate-pulse">Cargando el historial de actividades...</div>
          ) : progreso?.actividades && progreso.actividades.length > 0 ? (
            <div className="overflow-x-auto border rounded-xl border-gray-100">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr className="bg-gray-50/50">
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Actividad</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Calificación</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Origen</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {progreso.actividades.map((act, index) => (
                    <tr key={index} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{act.actividad}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {act.finalizado ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/50">
                            Finalizado
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200/50">
                            Pendiente
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {act.nota_numerica !== null ? (
                          <span className={`font-semibold inline-flex items-center space-x-1 ${act.aprobado ? 'text-emerald-600' : 'text-red-600'}`}>
                            <span>{act.nota_numerica}</span>
                            {act.aprobado ? (
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                            ) : null}
                          </span>
                        ) : act.nota_textual ? (
                          <span className={`font-semibold ${act.aprobado ? 'text-emerald-600' : 'text-red-600'}`}>
                            {act.nota_textual}
                          </span>
                        ) : (
                          <span className="text-gray-400 font-medium">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{act.origen}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
              <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>Aún no tenés actividades registradas en esta materia.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
