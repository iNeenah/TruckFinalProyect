import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  CircularProgress,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Business,
  Phone,
  PersonAdd,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import toast from 'react-hot-toast';

import { useAppDispatch, useAppSelector } from '@store/index';
import { register, clearError } from '@store/slices/authSlice';
import { RegisterRequest } from '@types/auth';

const schema = yup.object({
  full_name: yup
    .string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .required('El nombre completo es requerido'),
  email: yup
    .string()
    .email('Ingrese un email válido')
    .required('El email es requerido'),
  password: yup
    .string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'La contraseña debe contener al menos una mayúscula, una minúscula y un número'
    )
    .required('La contraseña es requerida'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden')
    .required('Confirme su contraseña'),
  company_name: yup.string().optional(),
  phone: yup.string().optional(),
  acceptTerms: yup
    .boolean()
    .oneOf([true], 'Debe aceptar los términos y condiciones'),
});

interface RegisterFormData extends RegisterRequest {
  confirmPassword: string;
  acceptTerms: boolean;
}

interface RegisterFormProps {
  onSuccess?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector((state) => state.auth);
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      full_name: '',
      email: '',
      password: '',
      confirmPassword: '',
      company_name: '',
      phone: '',
      acceptTerms: false,
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      dispatch(clearError());
      
      const registerData: RegisterRequest = {
        full_name: data.full_name,
        email: data.email,
        password: data.password,
        company_name: data.company_name || undefined,
        phone: data.phone || undefined,
      };
      
      const result = await dispatch(register(registerData));
      
      if (register.fulfilled.match(result)) {
        toast.success('¡Cuenta creada exitosamente!');
        if (onSuccess) {
          onSuccess();
        } else {
          navigate('/dashboard');
        }
      }
    } catch (err) {
      // Error is handled by the slice
    }
  };

  return (
    <Card sx={{ maxWidth: 500, mx: 'auto', mt: 4 }}>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <PersonAdd sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Crear Cuenta
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Complete el formulario para crear su cuenta
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <Controller
            name="full_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Nombre Completo"
                autoComplete="name"
                error={!!errors.full_name}
                helperText={errors.full_name?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Email"
                type="email"
                autoComplete="email"
                error={!!errors.email}
                helperText={errors.email?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="company_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Empresa (Opcional)"
                autoComplete="organization"
                error={!!errors.company_name}
                helperText={errors.company_name?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Business color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="phone"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Teléfono (Opcional)"
                type="tel"
                autoComplete="tel"
                error={!!errors.phone}
                helperText={errors.phone?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Phone color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="password"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                error={!!errors.password}
                helperText={errors.password?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="confirmPassword"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Confirmar Contraseña"
                type={showConfirmPassword ? 'text' : 'password'}
                autoComplete="new-password"
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        edge="end"
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />
            )}
          />

          <Controller
            name="acceptTerms"
            control={control}
            render={({ field }) => (
              <FormControlLabel
                control={
                  <Checkbox
                    {...field}
                    checked={field.value}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2">
                    Acepto los{' '}
                    <Link to="/terms" style={{ color: 'inherit' }}>
                      términos y condiciones
                    </Link>{' '}
                    y la{' '}
                    <Link to="/privacy" style={{ color: 'inherit' }}>
                      política de privacidad
                    </Link>
                  </Typography>
                }
                sx={{ mb: 2 }}
              />
            )}
          />
          {errors.acceptTerms && (
            <Typography variant="caption" color="error" sx={{ mb: 2, display: 'block' }}>
              {errors.acceptTerms.message}
            </Typography>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mb: 2, py: 1.5 }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Crear Cuenta'
            )}
          </Button>

          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary">
              ¿Ya tienes cuenta?
            </Typography>
          </Divider>

          <Button
            component={Link}
            to="/login"
            fullWidth
            variant="outlined"
            size="large"
            sx={{ py: 1.5 }}
          >
            Iniciar Sesión
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RegisterForm;