import React from 'react';
import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Logout } from '@mui/icons-material';

import { useAppDispatch, useAppSelector } from '@store/index';
import { logout } from '@store/slices/authSlice';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Optimizador de Rutas
          </Typography>
          
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
                Bienvenido, {user.full_name}
              </Typography>
              <Button
                color="inherit"
                startIcon={<Logout />}
                onClick={handleLogout}
              >
                Salir
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;