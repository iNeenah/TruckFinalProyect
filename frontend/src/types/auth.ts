// Authentication related types

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
  phone?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  company_id: string | null;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface TokenPayload {
  sub: string; // user id
  email: string;
  role: UserRole;
  company_id: string | null;
  exp: number;
  iat: number;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export type UserRole = 'admin' | 'operator';

export interface Permission {
  name: string;
  description: string;
}

export interface RolePermissions {
  role: UserRole;
  permissions: Permission[];
}