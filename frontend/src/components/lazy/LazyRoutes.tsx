import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@contexts/AuthContext';
import Layout from '@components/layout/Layout';
import MainLayout from '@components/layout/MainLayout';

// Importar componentes lazy
import {
  LazyAdminPanel,
  LazyReports,
  LazyVehicles,
  LazyRoutes as LazyRouteCalculator,
  LazyDashboard,
  LazyLogin,
  LazyRegister,
  LazyTolls,
  LazyFuelPrices,
  LazyUsers
} from './LazyComponents';

// Componente para rutas protegidas
const ProtectedRoute = ({ children, requiredRole }: { children: React.ReactNode; requiredRole?: string }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

// Componente para rutas públicas
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

const LazyRoutes = () => {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LazyLogin />
          </PublicRoute>
        } 
      />
      <Route 
        path="/register" 
        element={
          <PublicRoute>
            <LazyRegister />
          </PublicRoute>
        } 
      />
      
      {/* Rutas protegidas */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout>
              <MainLayout />
            </Layout>
          </ProtectedRoute>
        }
      >
        <Route index element={<LazyDashboard />} />
        <Route path="routes" element={<LazyRouteCalculator />} />
        <Route path="vehicles" element={<LazyVehicles />} />
        <Route path="reports" element={<LazyReports />} />
        
        {/* Rutas de administración */}
        <Route 
          path="admin" 
          element={
            <ProtectedRoute requiredRole="admin">
              <LazyAdminPanel />
            </ProtectedRoute>
          } 
        >
          <Route path="tolls" element={<LazyTolls />} />
          <Route path="fuel-prices" element={<LazyFuelPrices />} />
          <Route path="users" element={<LazyUsers />} />
        </Route>
      </Route>
      
      {/* Ruta por defecto */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default LazyRoutes;