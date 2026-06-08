import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useCommission } from '../pages/ComisionDashboard';
import { comunicacionesService } from '../services/comunicaciones.service';
import type { ComunicacionPreview } from '../services/comunicaciones.service';

export const TabComunicaciones = () => {
  const { materiaId, cohorteId } = useCommission();
  const [alumnosIds, setAlumnosIds] = useState<string>(''); // Comma separated for demo
  const [asunto, setAsunto] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [previewData, setPreviewData] = useState<ComunicacionPreview[] | null>(null);
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);

  const previewMutation = useMutation({
    mutationFn: () => comunicacionesService.previewMensaje(materiaId, cohorteId, {
      alumnos_ids: alumnosIds.split(',').map(s => s.trim()).filter(Boolean),
      asunto,
      mensaje,
      tipo: 'RECORDATORIO',
    }),
    onSuccess: (data) => setPreviewData(data),
  });

  const enviarMutation = useMutation({
    mutationFn: () => comunicacionesService.enviarLote(materiaId, cohorteId, {
      alumnos_ids: alumnosIds.split(',').map(s => s.trim()).filter(Boolean),
      asunto,
      mensaje,
      tipo: 'RECORDATORIO',
    }),
    onSuccess: (data) => {
      setActiveBatchId(data.batch_id);
      setPreviewData(null);
      setAsunto('');
      setMensaje('');
      setAlumnosIds('');
    }
  });

  // Polling para lote activo
  const { data: batchStatus } = useQuery({
    queryKey: ['batchStatus', activeBatchId],
    queryFn: () => comunicacionesService.getLoteStatus(activeBatchId!),
    enabled: !!activeBatchId,
    refetchInterval: (query) => {
      const state = query.state.data?.estado;
      // Continuar polling mientras esté PENDIENTE o ENVIANDO
      if (state === 'PENDIENTE' || state === 'ENVIANDO') return 5000;
      return false;
    },
  });

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Formulario de envío */}
      <section className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-800">Nueva Comunicación</h3>
        
        <div>
          <label className="block text-sm font-medium text-slate-700">Padrón de Alumnos (separados por coma)</label>
          <input 
            type="text" 
            value={alumnosIds} 
            onChange={e => setAlumnosIds(e.target.value)}
            placeholder="Ej: 12345, 67890"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Asunto</label>
          <input 
            type="text" 
            value={asunto} 
            onChange={e => setAsunto(e.target.value)}
            placeholder="Aviso de tareas faltantes"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Mensaje Template</label>
          <textarea 
            value={mensaje} 
            onChange={e => setMensaje(e.target.value)}
            rows={4}
            placeholder="Hola {{nombre}}, notamos que tienes tareas pendientes."
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
          />
          <p className="mt-1 text-xs text-slate-500">Variables disponibles: {`{{nombre}}, {{apellido}}, {{tareas_faltantes}}`}</p>
        </div>

        <button 
          onClick={() => previewMutation.mutate()}
          disabled={!alumnosIds || !asunto || !mensaje || previewMutation.isPending}
          className="bg-indigo-600 text-white px-4 py-2 rounded shadow hover:bg-indigo-700 disabled:opacity-50"
        >
          {previewMutation.isPending ? 'Cargando...' : 'Previsualizar'}
        </button>
      </section>

      {/* Previsualización y Tracking */}
      <section className="bg-slate-50 p-6 rounded-lg border border-slate-200">
        {previewData && (
          <div className="space-y-4">
            <h4 className="font-semibold text-slate-800">Previsualización</h4>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {previewData.map(p => (
                <div key={p.padron_id} className="bg-white p-3 rounded shadow-sm border border-slate-100 text-sm">
                  <p className="font-medium text-slate-700">A: {p.email}</p>
                  <p className="text-slate-600 font-medium border-b pb-1 mb-1">{p.asunto_preview}</p>
                  <p className="text-slate-600 whitespace-pre-wrap">{p.mensaje_preview}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => enviarMutation.mutate()}
              disabled={enviarMutation.isPending}
              className="w-full bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700 disabled:opacity-50"
            >
              Confirmar y Enviar Lote
            </button>
          </div>
        )}

        {batchStatus && (
          <div className="mt-6 border-t border-slate-200 pt-6">
            <h4 className="font-semibold text-slate-800 mb-4">Estado del Lote de Envío</h4>
            <div className="bg-white p-4 rounded shadow-sm border border-slate-100">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-500">ID Lote:</span>
                <span className="text-sm font-mono">{batchStatus.batch_id.split('-')[0]}...</span>
              </div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm font-medium text-slate-500">Estado:</span>
                <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 
                  ${batchStatus.estado === 'ENVIADO' ? 'bg-green-100 text-green-800' : 
                    batchStatus.estado === 'FALLIDO' ? 'bg-red-100 text-red-800' : 
                    'bg-yellow-100 text-yellow-800 animate-pulse'}`}>
                  {batchStatus.estado}
                </span>
              </div>

              {/* Progress bar */}
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                      Progreso
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold inline-block text-indigo-600">
                      {Math.round(((batchStatus.enviados + batchStatus.fallidos) / batchStatus.total) * 100)}%
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
                  <div style={{ width: `${(batchStatus.enviados / batchStatus.total) * 100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500"></div>
                  <div style={{ width: `${(batchStatus.fallidos / batchStatus.total) * 100}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-red-500"></div>
                </div>
                <p className="text-xs text-center text-slate-500">
                  {batchStatus.enviados} enviados, {batchStatus.fallidos} fallidos de {batchStatus.total} total
                </p>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};
