// Company related types

export interface Company {
  id: string;
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  tax_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCompanyRequest {
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  tax_id?: string;
}

export interface UpdateCompanyRequest {
  name?: string;
  address?: string;
  phone?: string;
  email?: string;
  tax_id?: string;
  is_active?: boolean;
}

export interface CompanyStats {
  total_users: number;
  active_users: number;
  total_vehicles: number;
  active_vehicles: number;
  total_routes: number;
  total_distance: number;
  total_cost: number;
  total_savings: number;
  routes_this_month: number;
  savings_this_month: number;
  top_users: CompanyTopUser[];
  top_vehicles: CompanyTopVehicle[];
}

export interface CompanyTopUser {
  user_id: string;
  user_name: string;
  route_count: number;
  total_distance: number;
  total_savings: number;
}

export interface CompanyTopVehicle {
  vehicle_id: string;
  vehicle_name: string;
  route_count: number;
  total_distance: number;
  total_cost: number;
}

export interface CompanySettings {
  company_id: string;
  default_fuel_type: string;
  default_optimization: 'cost' | 'time' | 'distance';
  auto_approve_routes: boolean;
  require_vehicle_selection: boolean;
  max_route_alternatives: number;
  enable_toll_avoidance: boolean;
  notification_settings: CompanyNotificationSettings;
}

export interface CompanyNotificationSettings {
  route_completion_emails: boolean;
  weekly_reports: boolean;
  monthly_reports: boolean;
  price_update_alerts: boolean;
  system_maintenance_alerts: boolean;
}