import React from 'react';
import { Container, Box, Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

import RegisterForm from '@components/auth/RegisterForm';
import ProtectedRoute from '@components/auth/ProtectedRoute';

const StyledContainer = styled(Container)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: `linear-gradient(135deg, ${theme.palette.secondary.light} 0%, ${theme.palette.secondary.main} 100%)`,
  padding: theme.spacing(2),
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  borderRadius: theme.spacing(2),
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  backdropFilter: 'blur(10px)',
  background: 'rgba(255, 255, 255, 0.95)',
  maxWidth: 600,
  width: '100%',
}));

const RegisterPage: React.FC = () => {
  return (
    <ProtectedRoute requireAuth={false}>
      <StyledContainer maxWidth={false}>
        <Box sx={{ width: '100%', maxWidth: 600 }}>
          <StyledPaper elevation={0}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 'bold',
                  background: 'linear-gradient(45deg, #388e3c, #1976d2)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Únete a Nosotros
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Crea tu cuenta y comienza a optimizar tus rutas
              </Typography>
            </Box>
            
            <RegisterForm />
          </StyledPaper>
        </Box>
      </StyledContainer>
    </ProtectedRoute>
  );
};

export default RegisterPage;