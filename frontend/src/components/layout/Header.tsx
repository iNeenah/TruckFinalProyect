import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import {
  BellIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

function Header() {
  const { user, logout } = useAuth();
  const { theme, setTheme, toggleTheme } = useTheme();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <SunIcon className="w-5 h-5" />;
      case 'dark':
        return <MoonIcon className="w-5 h-5" />;
      default:
        return <ComputerDesktopIcon className="w-5 h-5" />;
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return 'Claro';
      case 'dark':
        return 'Oscuro';
      default:
        return 'Sistema';
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left side - could add breadcrumbs or page title here */}
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              Optimizador de Rutas
            </h1>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
              <BellIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              {/* Notification badge */}
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Theme Toggle */}
            <div className="relative">
              <button
                onClick={() => setShowThemeMenu(!showThemeMenu)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                {getThemeIcon()}
                <span className="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
                  {getThemeLabel()}
                </span>
                <ChevronDownIcon className="w-4 h-4 text-gray-500" />
              </button>

              {showThemeMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                  <div className="py-2">
                    <button
                      onClick={() => {
                        setTheme('light');
                        setShowThemeMenu(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <SunIcon className="w-4 h-4 mr-3" />
                      Claro
                    </button>
                    <button
                      onClick={() => {
                        setTheme('dark');
                        setShowThemeMenu(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <MoonIcon className="w-4 h-4 mr-3" />
                      Oscuro
                    </button>
                    <button
                      onClick={() => {
                        setTheme('system');
                        setShowThemeMenu(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <ComputerDesktopIcon className="w-4 h-4 mr-3" />
                      Sistema
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.first_name?.[0]?.toUpperCase() || user?.email[0].toUpperCase()}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.email}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
                  </p>
                </div>
                <ChevronDownIcon className="w-4 h-4 text-gray-500" />
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                  <div className="py-2">
                    <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.email}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
                      {user?.company && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {user.company.name}
                        </p>
                      )}
                    </div>
                    
                    <button className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                      <UserCircleIcon className="w-4 h-4 mr-3" />
                      Perfil
                    </button>
                    
                    <button
                      onClick={() => {
                        logout();
                        setShowUserMenu(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      <ArrowRightOnRectangleIcon className="w-4 h-4 mr-3" />
                      Cerrar Sesión
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;