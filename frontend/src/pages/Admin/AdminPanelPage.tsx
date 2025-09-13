import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  CogIcon,
  UsersIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface AdminCardProps {
  title: string;
  description: string;
  icon: React.ElementType;
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  onClick: () => void;
  comingSoon?: boolean;
}

function AdminCard({ title, description, icon: Icon, color, onClick, comingSoon }: AdminCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 hover:border-blue-300',
    green: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 hover:border-green-300',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 hover:border-yellow-300',
    red: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 hover:border-red-300',
    purple: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 hover:border-purple-300',
  };

  const iconColorClasses = {
    blue: 'text-blue-600 dark:text-blue-400',
    green: 'text-green-600 dark:text-green-400',
    yellow: 'text-yellow-600 dark:text-yellow-400',
    red: 'text-red-600 dark:text-red-400',
    purple: 'text-purple-600 dark:text-purple-400',
  };

  return (
    <button
      onClick={onClick}
      disabled={comingSoon}
      className={`w-full text-left border rounded-lg p-6 transition-all ${colorClasses[color]} ${
        comingSoon ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md cursor-pointer'
      }`}
    >
      <div className="flex items-center">
        <div className={`p-3 rounded-lg bg-white dark:bg-gray-800 ${iconColorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="ml-4 flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
          {comingSoon && (
            <span className="inline-flex items-center mt-2 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
              Próximamente
            </span>
          )}
        </div>
      </div>
    </button>
  );
}

function AdminPanelPage() {
  const { user } = useAuth();
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="mx-auto h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Acceso Denegado
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            No tienes permisos para acceder al panel de administración.
          </p>
        </div>
      </div>
    );
  }

  const adminSections = [
    {
      id: 'users',
      title: 'Gestión de Usuarios',
      description: 'Administrar usuarios y empresas del sistema',
      icon: UsersIcon,
      color: 'blue' as const,
      comingSoon: true,
    },
    {
      id: 'tolls',
      title: 'Gestión de Peajes',
      description: 'Configurar tarifas y ubicaciones de peajes',
      icon: MapPinIcon,
      color: 'green' as const,
      comingSoon: true,
    },
    {
      id: 'fuel-prices',
      title: 'Precios de Combustible',
      description: 'Actualizar precios de combustible por región',
      icon: CurrencyDollarIcon,
      color: 'yellow' as const,
      comingSoon: true,
    },
    {
      id: 'system-config',
      title: 'Configuración del Sistema',
      description: 'Configuraciones generales y parámetros del sistema',
      icon: CogIcon,
      color: 'purple' as const,
      comingSoon: true,
    },
    {
      id: 'analytics',
      title: 'Análisis y Reportes',
      description: 'Estadísticas de uso y reportes del sistema',
      icon: ChartBarIcon,
      color: 'red' as const,
      comingSoon: true,
    },
  ];

  const handleSectionClick = (sectionId: string) => {
    setSelectedSection(sectionId);
    // Implement navigation to specific admin section
    console.log('Navigate to admin section:', sectionId);
    
    // In a real implementation, this would navigate to the specific section
    // For now, we'll show an alert with the section that would be navigated to
    const sectionNames: Record<string, string> = {
      tolls: 'Gestión de Peajes',
      fuelPrices: 'Precios de Combustible',
      users: 'Gestión de Usuarios',
      companies: 'Gestión de Empresas',
      vehicles: 'Gestión de Vehículos',
      reports: 'Reportes del Sistema',
      settings: 'Configuración del Sistema'
    };
    
    const sectionName = sectionNames[sectionId] || 'Sección Desconocida';
    alert(`En una implementación completa, esto navegaría a: ${sectionName}`);
    
    // In a real app, you would use React Router to navigate:
    // navigate(`/admin/${sectionId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Panel de Administración
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Gestiona configuraciones del sistema y datos maestros
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
              <span className="text-xs font-bold text-red-600 dark:text-red-400">A</span>
            </div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Administrador
            </span>
          </div>
        </div>
      </div>

      {/* Admin Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {adminSections.map((section) => (
          <AdminCard
            key={section.id}
            title={section.title}
            description={section.description}
            icon={section.icon}
            color={section.color}
            onClick={() => handleSectionClick(section.id)}
            comingSoon={section.comingSoon}
          />
        ))}
      </div>

      {/* System Status */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Estado del Sistema
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">API Backend</h3>
            <p className="text-sm text-green-600 dark:text-green-400">Operativo</p>
          </div>
          
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">Base de Datos</h3>
            <p className="text-sm text-green-600 dark:text-green-400">Conectada</p>
          </div>
          
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-full mb-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            </div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">OSRM Service</h3>
            <p className="text-sm text-yellow-600 dark:text-yellow-400">Verificando...</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Actividad Reciente
        </h2>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900 dark:text-white">
                Nuevo usuario registrado: empresa@ejemplo.com
              </span>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">Hace 2 horas</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900 dark:text-white">
                15 rutas calculadas en la última hora
              </span>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">Hace 1 hora</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-900 dark:text-white">
                Actualización de precios de combustible pendiente
              </span>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">Hace 6 horas</span>
          </div>
        </div>
      </div>

      {/* Coming Soon Notice */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <div className="flex items-center">
          <CogIcon className="w-8 h-8 text-blue-600 dark:text-blue-400 mr-4" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200">
              Funcionalidades en Desarrollo
            </h3>
            <p className="text-blue-700 dark:text-blue-300 mt-1">
              Las funcionalidades de administración están siendo desarrolladas. 
              Pronto podrás gestionar usuarios, peajes, precios de combustible y más.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminPanelPage;