import React from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
} from '@mui/material';
import {
  DirectionsCar,
  Route,
  Assessment,
  Settings,
} from '@mui/icons-material';

import { useAppSelector } from '@store/index';

const DashboardPage: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);

  const dashboardCards = [
    {
      title: 'Vehículos',
      description: 'Gestiona tu flota de vehículos',
      icon: <DirectionsCar sx={{ fontSize: 48, color: 'primary.main' }} />,
      path: '/vehicles',
      color: 'primary.light',
    },
    {
      title: 'Rutas',
      description: 'Calcula y optimiza rutas',
      icon: <Route sx={{ fontSize: 48, color: 'secondary.main' }} />,
      path: '/routes',
      color: 'secondary.light',
    },
    {
      title: 'Reportes',
      description: 'Visualiza estadísticas y reportes',
      icon: <Assessment sx={{ fontSize: 48, color: 'info.main' }} />,
      path: '/reports',
      color: 'info.light',
    },
    {
      title: 'Administración',
      description: 'Configuración del sistema',
      icon: <Settings sx={{ fontSize: 48, color: 'warning.main' }} />,
      path: '/admin',
      color: 'warning.light',
      adminOnly: true,
    },
  ];

  const visibleCards = dashboardCards.filter(
    (card) => !card.adminOnly || user?.role === 'admin'
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Bienvenido al sistema de optimización de rutas
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {visibleCards.map((card) => (
          <Grid item xs={12} sm={6} md={4} key={card.title}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    mb: 2,
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: card.color,
                    opacity: 0.1,
                  }}
                >
                  {card.icon}
                </Box>
                
                <Typography variant="h5" component="h2" gutterBottom>
                  {card.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {card.description}
                </Typography>
                
                <Button
                  variant="contained"
                  fullWidth
                  href={card.path}
                  sx={{ mt: 'auto' }}
                >
                  Acceder
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 6, p: 3, backgroundColor: 'background.paper', borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Estado del Sistema
        </Typography>
        <Typography variant="body1" color="text.secondary">
          El sistema está funcionando correctamente. Todas las funcionalidades están disponibles.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Última actualización: {new Date().toLocaleDateString('es-AR')}
        </Typography>
      </Box>
    </Container>
  );
};

export default DashboardPage;