import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  MapIcon,
  TruckIcon,
  DocumentChartBarIcon,
  CogIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Rutas', href: '/routes', icon: MapIcon },
  { name: 'Vehículos', href: '/vehicles', icon: TruckIcon },
  { name: 'Reportes', href: '/reports', icon: DocumentChartBarIcon },
];

const adminNavigation = [
  { name: 'Administración', href: '/admin', icon: CogIcon },
];

function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const isAdmin = user?.role === 'admin';

  return (
    <div className={`bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      <div className="h-full flex flex-col">
        {/* Logo */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          {!isCollapsed && (
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <MapIcon className="w-5 h-5 text-white" />
              </div>
              <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">
                Misiones
              </span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {isCollapsed ? (
              <ChevronRightIcon className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronLeftIcon className="w-5 h-5 text-gray-500" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                title={isCollapsed ? item.name : undefined}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!isCollapsed && <span className="ml-3">{item.name}</span>}
              </Link>
            );
          })}

          {/* Admin Section */}
          {isAdmin && (
            <>
              <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                {!isCollapsed && (
                  <p className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Administración
                  </p>
                )}
              </div>
              {adminNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                    title={isCollapsed ? item.name : undefined}
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {!isCollapsed && <span className="ml-3">{item.name}</span>}
                  </Link>
                );
              })}
            </>
          )}
        </nav>

        {/* User info */}
        {!isCollapsed && user && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {user.first_name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                </span>
              </div>
              <div className="ml-3 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user.first_name ? `${user.first_name} ${user.last_name}` : user.email}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user.company?.name || 'Sin empresa'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar;