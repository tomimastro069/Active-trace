import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { perfilService } from '../services/perfil.service';
import type { PerfilUpdatePayload } from '../types/perfil.types';

const CAMPOS: Array<{ key: keyof PerfilUpdatePayload; label: string }> = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'apellidos', label: 'Apellidos' },
  { key: 'email', label: 'Email' },
  { key: 'dni', label: 'DNI' },
  { key: 'banco', label: 'Banco' },
  { key: 'cbu', label: 'CBU' },
  { key: 'alias_cbu', label: 'Alias CBU' },
  { key: 'regional', label: 'Regional' },
  { key: 'legajo_profesional', label: 'Identificador profesional' },
  { key: 'modalidad_cobro', label: 'Modalidad de cobro' },
];

export const PerfilPage = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<PerfilUpdatePayload>({});
  const [feedback, setFeedback] = useState<string | null>(null);

  const { data: perfil, isLoading, isError } = useQuery({
    queryKey: ['mi-perfil'],
    queryFn: perfilService.getMiPerfil,
  });

  useEffect(() => {
    if (perfil) {
      setForm({
        nombre: perfil.nombre ?? '',
        apellidos: perfil.apellidos ?? '',
        email: perfil.email ?? '',
        dni: perfil.dni ?? '',
        banco: perfil.banco ?? '',
        cbu: perfil.cbu ?? '',
        alias_cbu: perfil.alias_cbu ?? '',
        regional: perfil.regional ?? '',
        legajo_profesional: perfil.legajo_profesional ?? '',
        modalidad_cobro: perfil.modalidad_cobro ?? '',
      });
    }
  }, [perfil]);

  const mutation = useMutation({
    mutationFn: (payload: PerfilUpdatePayload) => perfilService.actualizarMiPerfil(payload),
    onSuccess: () => {
      setFeedback('Perfil actualizado correctamente.');
      queryClient.invalidateQueries({ queryKey: ['mi-perfil'] });
    },
    onError: () => setFeedback('No se pudo actualizar el perfil.'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);
    mutation.mutate(form);
  };

  if (isLoading) return <div className="p-8 text-slate-500">Cargando perfil...</div>;
  if (isError) return <div className="p-8 text-red-500">Error al cargar el perfil.</div>;

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <header className="border-b border-slate-100 pb-4">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Mi Perfil</h1>
        <p className="text-slate-500 mt-1">Actualizá tus datos personales y bancarios.</p>
      </header>

      {feedback && (
        <div className="rounded-xl border border-indigo-100 bg-indigo-50/60 px-4 py-3 text-sm text-indigo-800">
          {feedback}
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {CAMPOS.map(({ key, label }) => (
          <div key={key}>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">{label}</label>
            <input
              type="text"
              value={(form[key] as string) ?? ''}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        ))}

        <div>
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">CUIL (solo lectura)</label>
          <input
            type="text"
            value={perfil?.cuil ?? ''}
            readOnly
            className="w-full rounded-xl border border-slate-200 bg-slate-100 px-3.5 py-2 text-sm text-slate-500"
          />
        </div>

        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="mt-2 inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 disabled:opacity-50"
          >
            {mutation.isPending ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  );
};
