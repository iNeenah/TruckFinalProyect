import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Components
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ConnectionStatus from './components/UI/ConnectionStatus';

// Pages
import LoginPage from './pages/Auth/LoginPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import RouteCalculatorPage from './pages/Routes/RouteCalculatorPage';
import VehicleManagementPage from './pages/Vehicles/VehicleManagementPage';
import AdminPanelPage from './pages/Admin/AdminPanelPage';
import NotFoundPage from './pages/NotFound/NotFoundPage';

// Styles
import './styles/globals.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginPage />} />
                
                {/* Protected Routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout>
                      <Navigate to="/dashboard" replace />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Layout>
                      <DashboardPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                <Route path="/routes" element={
                  <ProtectedRoute>
                    <Layout>
                      <RouteCalculatorPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                <Route path="/vehicles" element={
                  <ProtectedRoute>
                    <Layout>
                      <VehicleManagementPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                <Route path="/admin" element={
                  <ProtectedRoute requiredRole="admin">
                    <Layout>
                      <AdminPanelPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                {/* 404 Route */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
              
              {/* Global Components */}
              <ConnectionStatus />
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                }}
              />
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
      
      {/* React Query Devtools (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}

export default App;