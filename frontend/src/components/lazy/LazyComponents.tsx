import React, { lazy, Suspense } from 'react';
import { CircularProgress, Box } from '@mui/material';

// Componente para mostrar mientras se carga un componente lazy
const LoadingComponent = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
    <CircularProgress />
  </Box>
);

// Componentes lazy para code splitting
const LazyAdminPanelPage = lazy(() => import('@pages/Admin/AdminPanelPage'));
const LazyReportsPage = lazy(() => import('@pages/Reports/ReportsPage'));
const LazyVehicleManagementPage = lazy(() => import('@pages/Vehicles/VehicleManagementPage'));
const LazyRouteCalculatorPage = lazy(() => import('@pages/Routes/RouteCalculatorPage'));
const LazyDashboardPage = lazy(() => import('@pages/DashboardPage'));
const LazyLoginPage = lazy(() => import('@pages/Auth/LoginPage'));
const LazyRegisterPage = lazy(() => import('@pages/Auth/RegisterPage'));

// Componentes lazy con Suspense
export const LazyAdminPanel = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyAdminPanelPage />
  </Suspense>
);

export const LazyReports = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyReportsPage />
  </Suspense>
);

export const LazyVehicles = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyVehicleManagementPage />
  </Suspense>
);

export const LazyRoutes = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyRouteCalculatorPage />
  </Suspense>
);

export const LazyDashboard = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyDashboardPage />
  </Suspense>
);

export const LazyLogin = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyLoginPage />
  </Suspense>
);

export const LazyRegister = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyRegisterPage />
  </Suspense>
);

// Componentes lazy para secciones específicas
const LazyTollsManagement = lazy(() => import('@components/Admin/TollsManagement'));
const LazyFuelPricesManagement = lazy(() => import('@components/Admin/FuelPricesManagement'));
const LazyUserManagement = lazy(() => import('@components/Admin/UserManagement'));

export const LazyTolls = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyTollsManagement />
  </Suspense>
);

export const LazyFuelPrices = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyFuelPricesManagement />
  </Suspense>
);

export const LazyUsers = () => (
  <Suspense fallback={<LoadingComponent />}>
    <LazyUserManagement />
  </Suspense>
);