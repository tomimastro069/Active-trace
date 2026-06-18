import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mensajeriaService } from '../services/mensajeria.service';

export const InboxPage = () => {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [respuesta, setRespuesta] = useState('');

  const { data: threads, isLoading } = useQuery({
    queryKey: ['inbox-threads'],
    queryFn: mensajeriaService.getThreads,
  });

  const { data: thread } = useQuery({
    queryKey: ['inbox-thread', selectedId],
    queryFn: () => mensajeriaService.getThread(selectedId as string),
    enabled: !!selectedId,
  });

  const replyMutation = useMutation({
    mutationFn: (contenido: string) => mensajeriaService.responder(selectedId as string, contenido),
    onSuccess: () => {
      setRespuesta('');
      queryClient.invalidateQueries({ queryKey: ['inbox-thread', selectedId] });
      queryClient.invalidateQueries({ queryKey: ['inbox-threads'] });
    },
  });

  return (
    <div className="p-8 space-y-6 max-w-6xl mx-auto">
      <header className="border-b border-slate-100 pb-4">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Mensajería Interna</h1>
        <p className="text-slate-500 mt-1">Tus conversaciones con coordinación y el equipo.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 font-bold text-slate-800">Conversaciones</div>
          {isLoading && <div className="p-4 text-sm text-slate-500">Cargando...</div>}
          {threads && threads.length === 0 && (
            <div className="p-4 text-sm text-slate-400">No tenés conversaciones.</div>
          )}
          <ul className="divide-y divide-slate-100">
            {threads?.map((t) => (
              <li key={t.id}>
                <button
                  onClick={() => setSelectedId(t.id)}
                  className={`w-full text-left px-4 py-3 text-sm hover:bg-slate-50 ${
                    selectedId === t.id ? 'bg-indigo-50 font-semibold text-indigo-800' : 'text-slate-700'
                  }`}
                >
                  {t.asunto}
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <section className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 flex flex-col min-h-[24rem]">
          {!selectedId && (
            <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
              Seleccioná una conversación.
            </div>
          )}
          {thread && (
            <>
              <div className="px-5 py-3 border-b border-slate-100 font-bold text-slate-800">{thread.asunto}</div>
              <div className="flex-1 p-5 space-y-3 overflow-y-auto">
                {thread.mensajes?.map((m) => (
                  <div key={m.id} className="rounded-xl bg-slate-50 px-4 py-2.5">
                    <p className="text-xs font-semibold text-slate-500">{m.remitente_nombre ?? 'Usuario'}</p>
                    <p className="text-sm text-slate-800 whitespace-pre-wrap">{m.contenido}</p>
                  </div>
                ))}
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (respuesta.trim()) replyMutation.mutate(respuesta.trim());
                }}
                className="p-4 border-t border-slate-100 flex gap-2"
              >
                <input
                  value={respuesta}
                  onChange={(e) => setRespuesta(e.target.value)}
                  placeholder="Escribí tu respuesta..."
                  className="flex-1 rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  disabled={replyMutation.isPending}
                  className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-50"
                >
                  Enviar
                </button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  );
};
