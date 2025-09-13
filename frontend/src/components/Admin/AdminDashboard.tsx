import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  UsersIcon,
  TruckIcon,
  MapIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../UI/LoadingSpinner';

interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalCompanies: number;
  totalVehicles: number;
  activeVehicles: number;
  totalRoutes: number;
  routesToday: number;
  totalSavings: number;
  dataAlerts: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
}

interface SystemAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  resolved: boolean;
}

function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading admin data
    const loadAdminData = async () => {
      try {
        setIsLoading(true);
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        setStats({
          totalUsers: 45,
          activeUsers: 38,
          totalCompanies: 12,
          totalVehicles: 156,
          activeVehicles: 142,
          totalRoutes: 2847,
          routesToday: 23,
          totalSavings: 1250000,
          dataAlerts: 3,
          systemHealth: 'warning',
        });

        setAlerts([
          {
            id: '1',
            type: 'warning',
            title: 'Fuel Price Data Outdated',
            message: 'Some fuel prices haven\'t been updated in over 30 days',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
            resolved: false,
          },
          {
            id: '2',
            type: 'error',
            title: 'OSRM Service Slow Response',
            message: 'Route calculation service is responding slowly',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
            resolved: false,
          },
          {
            id: '3',
            type: 'info',
            title: 'Database Backup Completed',
            message: 'Daily database backup completed successfully',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
            resolved: true,
          },
        ]);
      } catch (error) {
        console.error('Error loading admin data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadAdminData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount);
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'critical':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" message="Loading admin dashboard..." />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <p className="text-red-500 text-center">Failed to load admin data</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats.totalUsers.toLocaleString(),
      subtitle: `${stats.activeUsers} active`,
      icon: UsersIcon,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: 'Companies',
      value: stats.totalCompanies.toLocaleString(),
      subtitle: 'Registered',
      icon: ChartBarIcon,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      title: 'Vehicles',
      value: stats.totalVehicles.toLocaleString(),
      subtitle: `${stats.activeVehicles} active`,
      icon: TruckIcon,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
    {
      title: 'Routes Calculated',
      value: stats.totalRoutes.toLocaleString(),
      subtitle: `${stats.routesToday} today`,
      icon: MapIcon,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
    {
      title: 'Total Savings',
      value: formatCurrency(stats.totalSavings),
      subtitle: 'Generated',
      icon: CurrencyDollarIcon,
      color: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900',
    },
    {
      title: 'System Health',
      value: stats.systemHealth.charAt(0).toUpperCase() + stats.systemHealth.slice(1),
      subtitle: `${stats.dataAlerts} alerts`,
      icon: ExclamationTriangleIcon,
      color: getSystemHealthColor(stats.systemHealth),
      bgColor: stats.systemHealth === 'healthy' ? 'bg-green-100 dark:bg-green-900' : 
                stats.systemHealth === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900' : 
                'bg-red-100 dark:bg-red-900',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((card, index) => (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 hover:shadow-lg transition-shadow duration-200"
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-full ${card.bgColor}`}>
                <card.icon className={`h-6 w-6 ${card.color}`} />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {card.title}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {card.value}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {card.subtitle}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Alerts */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              System Alerts
            </h3>
          </div>
          <div className="p-6">
            {alerts.length > 0 ? (
              <div className="space-y-4">
                {alerts.slice(0, 5).map((alert) => (
                  <div
                    key={alert.id}
                    className={`flex items-start p-4 rounded-lg ${
                      alert.type === 'error' ? 'bg-red-50 dark:bg-red-900/20' :
                      alert.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
                      'bg-blue-50 dark:bg-blue-900/20'
                    } ${alert.resolved ? 'opacity-60' : ''}`}
                  >
                    <div className="flex-shrink-0">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <p className={`text-sm font-medium ${
                          alert.type === 'error' ? 'text-red-800 dark:text-red-200' :
                          alert.type === 'warning' ? 'text-yellow-800 dark:text-yellow-200' :
                          'text-blue-800 dark:text-blue-200'
                        }`}>
                          {alert.title}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatTimeAgo(alert.timestamp)}
                        </span>
                      </div>
                      <p className={`text-xs mt-1 ${
                        alert.type === 'error' ? 'text-red-700 dark:text-red-300' :
                        alert.type === 'warning' ? 'text-yellow-700 dark:text-yellow-300' :
                        'text-blue-700 dark:text-blue-300'
                      }`}>
                        {alert.message}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  No active alerts
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Recent Activity
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                    <UsersIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900 dark:text-white">
                    New user registered: Juan Pérez
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</p>
                </div>
              </div>

              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                    <TruckIcon className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900 dark:text-white">
                    Vehicle added: Truck-045
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">4 hours ago</p>
                </div>
              </div>

              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center">
                    <CurrencyDollarIcon className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900 dark:text-white">
                    Fuel prices updated
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">6 hours ago</p>
                </div>
              </div>

              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                    <MapIcon className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900 dark:text-white">
                    Route calculated: Posadas → Buenos Aires
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">8 hours ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200">
            <CurrencyDollarIcon className="h-5 w-5 mr-2" />
            Update Fuel Prices
          </button>
          <button className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200">
            <MapIcon className="h-5 w-5 mr-2" />
            Manage Tolls
          </button>
          <button className="flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200">
            <UsersIcon className="h-5 w-5 mr-2" />
            User Management
          </button>
          <button className="flex items-center justify-center px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200">
            <CogIcon className="h-5 w-5 mr-2" />
            System Settings
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;