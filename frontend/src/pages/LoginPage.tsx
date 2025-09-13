import React from 'react';
import { Container, Box, Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

import LoginForm from '@components/auth/LoginForm';
import ProtectedRoute from '@components/auth/ProtectedRoute';

const StyledContainer = styled(Container)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: `linear-gradient(135deg, ${theme.palette.primary.light} 0%, ${theme.palette.primary.main} 100%)`,
  padding: theme.spacing(2),
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  borderRadius: theme.spacing(2),
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  backdropFilter: 'blur(10px)',
  background: 'rgba(255, 255, 255, 0.95)',
  maxWidth: 500,
  width: '100%',
}));

const LoginPage: React.FC = () => {
  return (
    <ProtectedRoute requireAuth={false}>
      <StyledContainer maxWidth={false}>
        <Box sx={{ width: '100%', maxWidth: 500 }}>
          <StyledPaper elevation={0}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 'bold',
                  background: 'linear-gradient(45deg, #1976d2, #388e3c)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Optimizador de Rutas
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Sistema inteligente para optimización de rutas en Misiones
              </Typography>
            </Box>
            
            <LoginForm />
          </StyledPaper>
        </Box>
      </StyledContainer>
    </ProtectedRoute>
  );
};

export default LoginPage;