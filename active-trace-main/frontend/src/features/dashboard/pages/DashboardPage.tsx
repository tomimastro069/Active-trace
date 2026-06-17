import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/shared/contexts/AuthContext';
import { StatCard } from '../components/StatCard';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Hola, {user?.email || 'Docente'} 👋
        </h1>
        <p className="mt-2 text-gray-600">
          Este es el resumen de tu semana en Active Trace.
        </p>
      </div>

      {/* KPIs Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Alumnos atrasados"
          value={12}
          description="Requieren atención esta semana"
          trend="up"
          trendValue="+3 vs sem pasada"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
        />
        <StatCard
          title="Entregas sin corregir"
          value={5}
          description="En tus comisiones activas"
          trend="down"
          trendValue="-2 vs sem pasada"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          }
        />
        <StatCard
          title="Próximos encuentros"
          value={2}
          description="Agendados para esta semana"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
        />
      </div>

      {/* Main Grid: Comisiones y Acciones */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Mis Comisiones */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">Mis Comisiones</h2>
              <Link to="/comisiones" className="text-sm font-medium text-blue-600 hover:text-blue-500">Ver todas &rarr;</Link>
            </div>
            <div className="divide-y divide-gray-100">
              {/* Fake List */}
              <Link to="/comisiones/1/1" className="block p-6 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-md font-medium text-gray-900">Programación Avanzada</h3>
                    <p className="text-sm text-gray-500 mt-1">Comisión A • 24 alumnos</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      3 alertas
                    </span>
                    <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </Link>
              <Link to="/comisiones/1/2" className="block p-6 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-md font-medium text-gray-900">Bases de Datos</h3>
                    <p className="text-sm text-gray-500 mt-1">Comisión B • 30 alumnos</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Al día
                    </span>
                    <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>

        {/* Acciones Rápidas */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-900">Accesos Rápidos</h2>
          <div className="grid grid-cols-1 gap-4">
            <Link
              to="/equipos"
              className="flex items-center p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md hover:border-blue-100 transition-all group"
            >
              <div className="flex-shrink-0 bg-blue-50 p-3 rounded-lg group-hover:bg-blue-100 transition-colors">
                <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Equipos Docentes</h3>
                <p className="text-xs text-gray-500 mt-1">Gestionar profesores</p>
              </div>
            </Link>

            <Link
              to="/avisos"
              className="flex items-center p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md hover:indigo-100 transition-all group"
            >
              <div className="flex-shrink-0 bg-indigo-50 p-3 rounded-lg group-hover:bg-indigo-100 transition-colors">
                <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Avisos Institucionales</h3>
                <p className="text-xs text-gray-500 mt-1">Anuncios de coordinación</p>
              </div>
            </Link>

            <Link
              to="/tareas"
              className="flex items-center p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md hover:teal-100 transition-all group"
            >
              <div className="flex-shrink-0 bg-teal-50 p-3 rounded-lg group-hover:bg-teal-100 transition-colors">
                <svg className="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-900">Mis Tareas</h3>
                <p className="text-xs text-gray-500 mt-1">Actividades pendientes</p>
              </div>
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
};
