import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { avisosService } from '../services/avisos.service';
import type { AlcanceAviso, AvisoCreatePayload } from '../types/coordinacion.types';

const ALCANCES: AlcanceAviso[] = ['Global', 'PorMateria', 'PorCohorte', 'PorRol'];
const SEVERIDADES = ['info', 'warning', 'critical'];

const emptyAviso: AvisoCreatePayload = {
  alcance: 'Global',
  severidad: 'info',
  titulo: '',
  cuerpo: '',
  inicio_en: '',
  fin_en: '',
  orden: 0,
  requiere_ack: false,
};

export const AvisoForm = () => {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<AvisoCreatePayload>(emptyAviso);

  const mutation = useMutation({
    mutationFn: () => avisosService.crearAviso(form),
    onSuccess: () => {
      setForm(emptyAviso);
      queryClient.invalidateQueries({ queryKey: ['avisos-activos'] });
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        mutation.mutate();
      }}
      className="space-y-3 rounded-lg border border-slate-200 p-4"
    >
      <h3 className="text-base font-semibold text-slate-800">Publicar Aviso</h3>

      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm text-slate-600">
          Alcance
          <select
            value={form.alcance}
            onChange={(e) => setForm({ ...form, alcance: e.target.value as AlcanceAviso })}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          >
            {ALCANCES.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </label>
        <label className="text-sm text-slate-600">
          Severidad
          <select
            value={form.severidad}
            onChange={(e) => setForm({ ...form, severidad: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          >
            {SEVERIDADES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
      </div>

      {form.alcance === 'PorMateria' && (
        <input placeholder="Materia ID" value={form.materia_id ?? ''}
          onChange={(e) => setForm({ ...form, materia_id: e.target.value })}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      )}
      {form.alcance === 'PorCohorte' && (
        <input placeholder="Cohorte ID" value={form.cohorte_id ?? ''}
          onChange={(e) => setForm({ ...form, cohorte_id: e.target.value })}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      )}
      {form.alcance === 'PorRol' && (
        <input placeholder="Rol destino (ej. PROFESOR)" value={form.rol_destino ?? ''}
          onChange={(e) => setForm({ ...form, rol_destino: e.target.value })}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      )}

      <input required placeholder="Título" value={form.titulo}
        onChange={(e) => setForm({ ...form, titulo: e.target.value })}
        className="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
      <textarea required placeholder="Cuerpo del aviso" value={form.cuerpo}
        onChange={(e) => setForm({ ...form, cuerpo: e.target.value })}
        className="w-full rounded border border-slate-300 px-3 py-2 text-sm" rows={3} />

      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm text-slate-600">
          Inicio
          <input required type="datetime-local" value={form.inicio_en}
            onChange={(e) => setForm({ ...form, inicio_en: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm" />
        </label>
        <label className="text-sm text-slate-600">
          Fin
          <input required type="datetime-local" value={form.fin_en}
            onChange={(e) => setForm({ ...form, fin_en: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm" />
        </label>
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-600">
        <input type="checkbox" checked={form.requiere_ack}
          onChange={(e) => setForm({ ...form, requiere_ack: e.target.checked })} />
        Requiere confirmación de lectura
      </label>

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full rounded bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {mutation.isPending ? 'Publicando...' : 'Publicar Aviso'}
      </button>
      {mutation.isError && <p className="text-sm text-red-500">Error al publicar el aviso.</p>}
    </form>
  );
};
