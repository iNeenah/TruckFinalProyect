import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useMediaQuery, useTheme } from '@mui/material';

import { useAppDispatch } from '@store/index';
import { setIsMobile, setScreenSize } from '@store/slices/uiSlice';

import AuthGuard from '@components/auth/AuthGuard';
import ProtectedRoute from '@components/auth/ProtectedRoute';

// Pages
import LoginPage from '@pages/LoginPage';
import RegisterPage from '@pages/RegisterPage';
import DashboardPage from '@pages/DashboardPage';

// Layouts
import MainLayout from '@components/layout/MainLayout';

const App: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isXs = useMediaQuery(theme.breakpoints.only('xs'));
  const isSm = useMediaQuery(theme.breakpoints.only('sm'));
  const isMd = useMediaQuery(theme.breakpoints.only('md'));
  const isLg = useMediaQuery(theme.breakpoints.only('lg'));
  const isXl = useMediaQuery(theme.breakpoints.up('xl'));

  useEffect(() => {
    dispatch(setIsMobile(isMobile));
    
    let screenSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'md';
    if (isXs) screenSize = 'xs';
    else if (isSm) screenSize = 'sm';
    else if (isMd) screenSize = 'md';
    else if (isLg) screenSize = 'lg';
    else if (isXl) screenSize = 'xl';
    
    dispatch(setScreenSize(screenSize));
  }, [dispatch, isMobile, isXs, isSm, isMd, isLg, isXl]);

  return (
    <AuthGuard>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  
                  {/* Placeholder routes - will be implemented in later tasks */}
                  <Route path="/vehicles" element={<div>Vehicles Page (Coming Soon)</div>} />
                  <Route path="/routes" element={<div>Routes Page (Coming Soon)</div>} />
                  <Route path="/reports" element={<div>Reports Page (Coming Soon)</div>} />
                  <Route path="/admin" element={<div>Admin Page (Coming Soon)</div>} />
                  
                  {/* Catch all route */}
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </MainLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthGuard>
  );
};

export default App;