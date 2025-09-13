import React from 'react';
import {
  VehicleStats,
  formatFuelType,
  formatWeight,
  formatVolume,
  formatFuelConsumption,
} from '../../types/vehicle';
import {
  TruckIcon,
  CheckCircleIcon,
  XCircleIcon,
  BeakerIcon,
  ScaleIcon,
  CubeIcon,
} from '@heroicons/react/24/outline';

interface VehicleStatsCardsProps {
  stats: VehicleStats;
}

function VehicleStatsCards({ stats }: VehicleStatsCardsProps) {
  const statCards = [
    {
      title: 'Total Vehicles',
      value: stats.total_vehicles.toLocaleString(),
      icon: TruckIcon,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: 'Active Vehicles',
      value: stats.active_vehicles.toLocaleString(),
      icon: CheckCircleIcon,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      title: 'Inactive Vehicles',
      value: stats.inactive_vehicles.toLocaleString(),
      icon: XCircleIcon,
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-100 dark:bg-red-900',
    },
    {
      title: 'Avg Consumption',
      value: formatFuelConsumption(stats.avg_fuel_consumption),
      icon: BeakerIcon,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
    {
      title: 'Total Weight Capacity',
      value: formatWeight(stats.total_capacity_weight),
      icon: ScaleIcon,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
    {
      title: 'Total Volume Capacity',
      value: formatVolume(stats.total_capacity_volume),
      icon: CubeIcon,
      color: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="bg-white dark:bg-gray-800 shadow rounded-lg p-4 hover:shadow-lg transition-shadow duration-200"
        >
          <div className="flex items-center">
            <div className={`p-2 rounded-full ${card.bgColor}`}>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-600 dark:text-gray-400 truncate">
                {card.title}
              </p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {card.value}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default VehicleStatsCards;