import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

import { useAppDispatch, useAppSelector } from '@store/index';
import { getCurrentUser } from '@store/slices/authSlice';
import { authService } from '@services/authService';

interface AuthGuardProps {
  children: React.ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const { user, token, isLoading } = useAppSelector((state) => state.auth);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = authService.getToken();
        
        if (storedToken && !authService.isTokenExpired(storedToken)) {
          // Token exists and is valid, get current user
          if (!user) {
            await dispatch(getCurrentUser());
          }
        } else if (storedToken) {
          // Token exists but is expired, remove it
          authService.removeToken();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        authService.removeToken();
      } finally {
        setIsInitializing(false);
      }
    };

    initializeAuth();
  }, [dispatch, user]);

  // Show loading during initialization
  if (isInitializing || (token && !user && isLoading)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
          Inicializando aplicación...
        </Typography>
      </Box>
    );
  }

  return <>{children}</>;
};

export default AuthGuard;