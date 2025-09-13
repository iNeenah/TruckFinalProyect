import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRouteStatistics } from '../../hooks/useRoutes';
import { useVehicles } from '../../hooks/useVehicles';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  MapIcon,
  TruckIcon,
  CurrencyDollarIcon,
  ClockIcon,
  ChartBarIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  color: 'blue' | 'green' | 'yellow' | 'red';
  href?: string;
}

function StatCard({ title, value, subtitle, icon: Icon, color, href }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300',
    green: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300',
    red: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300',
  };

  const iconColorClasses = {
    blue: 'text-blue-600 dark:text-blue-400',
    green: 'text-green-600 dark:text-green-400',
    yellow: 'text-yellow-600 dark:text-yellow-400',
    red: 'text-red-600 dark:text-red-400',
  };

  const content = (
    <div className={`border rounded-lg p-6 ${colorClasses[color]} transition-colors hover:opacity-80`}>
      <div className="flex items-center">
        <div className={`p-3 rounded-lg bg-white dark:bg-gray-800 ${iconColorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );

  return href ? <Link to={href}>{content}</Link> : content;
}

function DashboardPage() {
  const { user } = useAuth();

  // Fetch statistics
  const { data: routeStats, isLoading: isLoadingStats } = useRouteStatistics();
  const { data: vehiclesData, isLoading: isLoadingVehicles } = useVehicles(
    { is_active: true },
    1,
    10
  );

  if (isLoadingStats || isLoadingVehicles) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const totalVehicles = vehiclesData?.total || 0;
  const activeVehicles = vehiclesData?.vehicles?.filter(v => v.is_active).length || 0;

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              ¡Bienvenido, {user?.first_name || user?.email}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Optimiza tus rutas y reduce costos de transporte
            </p>
          </div>
          <div className="hidden sm:block">
            <Link to="/routes" className="btn btn-primary">
              <PlusIcon className="w-5 h-5 mr-2" />
              Nueva Ruta
            </Link>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Rutas Calculadas"
          value={routeStats?.total_routes || 0}
          subtitle="Este mes"
          icon={MapIcon}
          color="blue"
          href="/routes"
        />
        
        <StatCard
          title="Vehículos Activos"
          value={activeVehicles}
          subtitle={`de ${totalVehicles} total`}
          icon={TruckIcon}
          color="green"
          href="/vehicles"
        />
        
        <StatCard
          title="Ahorro Total"
          value={`$${(routeStats?.total_savings || 0).toLocaleString()}`}
          subtitle="vs rutas más rápidas"
          icon={CurrencyDollarIcon}
          color="yellow"
        />
        
        <StatCard
          title="Tiempo Promedio"
          value={`${Math.round((routeStats?.avg_duration || 0) / 60)}min`}
          subtitle="por ruta"
          icon={ClockIcon}
          color="red"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Routes */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Rutas Recientes
            </h2>
            <Link to="/routes" className="text-blue-600 hover:text-blue-500 text-sm font-medium">
              Ver todas
            </Link>
          </div>
          
          {routeStats?.recent_routes && routeStats.recent_routes.length > 0 ? (
            <div className="space-y-3">
              {routeStats.recent_routes.slice(0, 5).map((route: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center">
                    <MapIcon className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {route.origin} → {route.destination}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(route.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    ${route.total_cost?.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <MapIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                No hay rutas calculadas aún
              </p>
              <Link to="/routes" className="btn btn-primary mt-4">
                Calcular primera ruta
              </Link>
            </div>
          )}
        </div>

        {/* Vehicle Status */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Estado de Vehículos
            </h2>
            <Link to="/vehicles" className="text-blue-600 hover:text-blue-500 text-sm font-medium">
              Gestionar
            </Link>
          </div>
          
          {vehiclesData?.vehicles && vehiclesData.vehicles.length > 0 ? (
            <div className="space-y-3">
              {vehiclesData.vehicles.slice(0, 5).map((vehicle) => (
                <div key={vehicle.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center">
                    <TruckIcon className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {vehicle.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {vehicle.license_plate} • {vehicle.fuel_type}
                      </p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    vehicle.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {vehicle.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <TruckIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                No hay vehículos registrados
              </p>
              <Link to="/vehicles" className="btn btn-primary mt-4">
                Agregar vehículo
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Charts Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Estadísticas del Mes
          </h2>
          <Link to="/reports" className="text-blue-600 hover:text-blue-500 text-sm font-medium">
            Ver reportes
          </Link>
        </div>
        
        <div className="text-center py-12">
          <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            Gráficos de estadísticas próximamente
          </p>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;