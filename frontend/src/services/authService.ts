import { 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest, 
  AuthUser,
  PasswordResetRequest,
  PasswordResetConfirm,
  ChangePasswordRequest
} from '@types/auth';
import { apiService } from './api';

class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await apiService.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response;
  }

  async register(userData: RegisterRequest): Promise<LoginResponse> {
    return await apiService.post<LoginResponse>('/auth/register', userData);
  }

  async getCurrentUser(): Promise<AuthUser> {
    return await apiService.get<AuthUser>('/auth/me');
  }

  async refreshToken(): Promise<LoginResponse> {
    return await apiService.post<LoginResponse>('/auth/refresh');
  }

  async logout(): Promise<void> {
    await apiService.post('/auth/logout');
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await apiService.post('/auth/password-reset', data);
  }

  async confirmPasswordReset(data: PasswordResetConfirm): Promise<void> {
    await apiService.post('/auth/password-reset/confirm', data);
  }

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await apiService.post('/auth/change-password', data);
  }

  // Token management
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  setToken(token: string): void {
    localStorage.setItem('token', token);
  }

  removeToken(): void {
    localStorage.removeItem('token');
  }

  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null && !this.isTokenExpired(token);
  }
}

export const authService = new AuthService();
export default authService;