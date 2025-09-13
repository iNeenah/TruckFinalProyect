// User related types

import { UserRole } from './auth';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  company_id: string | null;
  phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
  company_id?: string;
  phone?: string;
}

export interface UpdateUserRequest {
  full_name?: string;
  phone?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  company_name?: string;
  role: UserRole;
  created_at: string;
  last_login?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  language: 'es' | 'en';
  theme: 'light' | 'dark';
  currency: 'ARS' | 'USD';
  distance_unit: 'km' | 'mi';
  notifications: NotificationPreferences;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  route_completion: boolean;
  price_updates: boolean;
  system_alerts: boolean;
}

export interface UpdateProfileRequest {
  full_name?: string;
  phone?: string;
  preferences?: Partial<UserPreferences>;
}

export interface UserStats {
  total_routes: number;
  total_distance: number;
  total_savings: number;
  average_cost_per_km: number;
  most_used_vehicle?: string;
  routes_this_month: number;
  savings_this_month: number;
}