import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { avisosService } from '../services/avisos.service';
import { AvisoForm } from '../components/AvisoForm';

const severityClasses: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-yellow-100 text-yellow-800',
  critical: 'bg-red-100 text-red-800',
};

export const AvisosPage = () => {
  const queryClient = useQueryClient();

  const { data: avisos, isLoading, isError } = useQuery({
    queryKey: ['avisos-activos'],
    queryFn: avisosService.getActivos,
  });

  const ackMutation = useMutation({
    mutationFn: (avisoId: string) => avisosService.acusarRecibo(avisoId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avisos-activos'] }),
  });

  return (
    <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-4">
        <header>
          <h1 className="text-2xl font-bold text-slate-800">Avisos Activos</h1>
          <p className="text-sm text-slate-500">Avisos vigentes según tu rol y contexto.</p>
        </header>

        {isLoading && <div className="text-slate-500">Cargando avisos...</div>}
        {isError && <div className="text-red-500">Error al cargar los avisos.</div>}

        {avisos && avisos.length === 0 && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 py-12 text-center text-slate-500">
            No hay avisos activos.
          </div>
        )}

        <div className="space-y-3">
          {avisos?.map((aviso) => (
            <article key={aviso.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <h2 className="font-semibold text-slate-800">{aviso.titulo}</h2>
                <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${severityClasses[aviso.severidad] ?? 'bg-slate-100 text-slate-700'}`}>
                  {aviso.severidad}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-600">{aviso.cuerpo}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-xs uppercase text-slate-400">{aviso.alcance}</span>
                {aviso.requiere_ack && (
                  <button
                    onClick={() => ackMutation.mutate(aviso.id)}
                    disabled={ackMutation.isPending}
                    className="rounded border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    Confirmar lectura
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      </div>

      <div>
        <AvisoForm />
      </div>
    </div>
  );
};
