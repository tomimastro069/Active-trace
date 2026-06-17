import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { equiposService } from '../services/equipos.service';

export const UsuariosPage = () => {
  const queryClient = useQueryClient();
  const [nuevoUser, setNuevoUser] = useState({
    email: '',
    password: '',
    nombre: '',
    apellidos: '',
    estado: 'Activo',
  });
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [feedback, setFeedback] = useState<string | null>(null);

  // Consulta de usuarios
  const { data: usuarios, isLoading, isError } = useQuery({
    queryKey: ['admin-usuarios'],
    queryFn: equiposService.getUsuarios,
  });
  const { data: roles, isLoading: rolesLoading } = useQuery({
    queryKey: ['admin-roles'],
    queryFn: equiposService.getRoles,
  });

  // Mutación para la creación de usuario
  const crearUserMutation = useMutation({
    mutationFn: (payload) => equiposService.crearUsuario(payload),
    onSuccess: async (createdUser) => {
      // Assign selected role to the newly created user
      if (selectedRole) {
        try {
          await equiposService.crearAsignacion({
            usuario_id: createdUser.id,
            rol_id: selectedRole,
            desde: new Date().toISOString(),
          });
          setFeedback('Usuario y asignación creados exitosamente.');
        } catch (e) {
          setFeedback('Usuario creado, pero falló la asignación de rol.');
        }
      } else {
        setFeedback('Usuario creado exitosamente (sin rol asignado).');
      }
      setNuevoUser({
        email: '',
        password: '',
        nombre: '',
        apellidos: '',
        estado: 'Activo',
      });
      setSelectedRole('');
      queryClient.invalidateQueries({ queryKey: ['admin-usuarios'] });
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
    },


    onError: () => {
      setFeedback('Error al crear el usuario. Verificá que el email no esté registrado.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole) {
      setFeedback('Debes seleccionar un rol antes de crear el usuario.');
      return;
    }
    crearUserMutation.mutate(nuevoUser);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto animate-fade-in">
      <header className="border-b border-slate-100 pb-6">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Gestión de Usuarios</h1>
        <p className="text-slate-500 mt-1">Creá y administrá las cuentas de docentes, coordinadores y administradores del tenant.</p>
      </header>

      {feedback && (
        <div className="flex items-center justify-between rounded-xl border border-indigo-100 bg-indigo-50/50 px-4 py-3 text-sm text-indigo-800 shadow-sm animate-fade-in">
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} className="text-indigo-500 hover:text-indigo-700 font-semibold">
            Cerrar
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Formulario de Alta (1/3 de ancho) */}
        <div className="lg:col-span-1">
          <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
              <span className="w-1.5 h-6 bg-indigo-600 rounded mr-2.5 inline-block"></span>
              Registrar Nuevo Usuario
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Email</label>
                <input
                  required
                  type="email"
                  placeholder="usuario@ejemplo.com"
                  value={nuevoUser.email}
                  onChange={(e) => setNuevoUser({ ...nuevoUser, email: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                {/* Role selector */}
                {rolesLoading ? (
                  <select disabled className="w-full mt-2 rounded-xl border border-slate-300 px-3.5 py-2 text-sm bg-gray-100">
                    <option>Cargando roles...</option>
                  </select>
                ) : (
                  <select
                    required
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full mt-2 rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="" disabled>Seleccioná un rol</option>
                    {roles && roles.map((rol: any) => (
                      <option key={rol.id} value={rol.id}>{rol.nombre}</option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Contraseña</label>
                <input
                  required
                  type="password"
                  placeholder="Mínimo 6 caracteres"
                  value={nuevoUser.password}
                  onChange={(e) => setNuevoUser({ ...nuevoUser, password: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Nombre</label>
                <input
                  required
                  type="text"
                  placeholder="Ej: Juan"
                  value={nuevoUser.nombre}
                  onChange={(e) => setNuevoUser({ ...nuevoUser, nombre: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Apellidos</label>
                <input
                  required
                  type="text"
                  placeholder="Ej: Pérez"
                  value={nuevoUser.apellidos}
                  onChange={(e) => setNuevoUser({ ...nuevoUser, apellidos: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Estado</label>
                <select
                  value={nuevoUser.estado}
                  onChange={(e) => setNuevoUser({ ...nuevoUser, estado: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white"
                >
                  <option value="Activo">Activo</option>
                  <option value="Inactivo">Inactivo</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={crearUserMutation.isPending}
                className="w-full mt-2 inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 active:bg-indigo-800 disabled:opacity-50 shadow-sm transition-all duration-150"
              >
                {crearUserMutation.isPending ? 'Registrando...' : 'Registrar Cuenta'}
              </button>
            </form>
          </section>
        </div>

        {/* Listado de Cuentas (2/3 de ancho) */}
        <div className="lg:col-span-2 space-y-4">
          <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900">Cuentas Registradas en el Tenant</h2>
              <span className="bg-slate-100 text-slate-600 text-xs font-semibold px-2.5 py-1 rounded-full">
                {usuarios ? `${usuarios.length} usuarios` : '0 usuarios'}
              </span>
            </div>

            {isLoading && (
              <div className="p-8 text-center text-slate-500">
                <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                Cargando cuentas...
              </div>
            )}

            {isError && (
              <div className="p-8 text-center text-red-500">
                Error al cargar el listado de usuarios.
              </div>
            )}

            {usuarios && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50/75">
                    <tr>
                      <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Nombre Completo</th>
                      <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Rol</th>
                      <th className="px-6 py-3.5 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {usuarios.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-400">
                          No hay usuarios registrados.
                        </td>
                      </tr>
                    )}
                    {usuarios.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-slate-900">
                          {u.nombre} {u.apellidos}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {u.email}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {u.role_nombre ?? 'Sin rol'}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold leading-5 ${
                            u.estado === 'Activo' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-500'
                          }`}>
                            {u.estado}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>

      </div>
    </div>
  );
};
