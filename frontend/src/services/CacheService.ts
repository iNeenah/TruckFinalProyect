import { Vehicle, CalculatedRoute, Toll, FuelPrice } from '@types';

class CacheService {
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();
  private defaultTTL = 5 * 60 * 1000; // 5 minutos por defecto

  // Establecer un valor en caché
  set<T>(key: string, data: T, ttl: number = this.defaultTTL): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  // Obtener un valor de caché
  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    
    if (!cached) {
      return null;
    }
    
    // Verificar si el caché ha expirado
    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data as T;
  }

  // Eliminar un valor de caché
  remove(key: string): void {
    this.cache.delete(key);
  }

  // Limpiar todo el caché
  clear(): void {
    this.cache.clear();
  }

  // Limpiar caché expirado
  clearExpired(): void {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > value.ttl) {
        this.cache.delete(key);
      }
    }
  }

  // Caché específico para vehículos
  cacheVehicles(vehicles: Vehicle[]): void {
    this.set<Vehicle[]>('vehicles', vehicles, 10 * 60 * 1000); // 10 minutos
  }

  getCachedVehicles(): Vehicle[] | null {
    return this.get<Vehicle[]>('vehicles');
  }

  // Caché específico para rutas guardadas
  cacheSavedRoutes(routes: CalculatedRoute[]): void {
    this.set<CalculatedRoute[]>('savedRoutes', routes, 5 * 60 * 1000); // 5 minutos
  }

  getCachedSavedRoutes(): CalculatedRoute[] | null {
    return this.get<CalculatedRoute[]>('savedRoutes');
  }

  // Caché específico para peajes
  cacheTolls(tolls: Toll[]): void {
    this.set<Toll[]>('tolls', tolls, 30 * 60 * 1000); // 30 minutos
  }

  getCachedTolls(): Toll[] | null {
    return this.get<Toll[]>('tolls');
  }

  // Caché específico para precios de combustible
  cacheFuelPrices(prices: FuelPrice[]): void {
    this.set<FuelPrice[]>('fuelPrices', prices, 60 * 60 * 1000); // 1 hora
  }

  getCachedFuelPrices(): FuelPrice[] | null {
    return this.get<FuelPrice[]>('fuelPrices');
  }

  // Caché para datos de autocompletado
  cacheAutocomplete(key: string, data: any[]): void {
    this.set<any[]>(`autocomplete_${key}`, data, 2 * 60 * 1000); // 2 minutos
  }

  getCachedAutocomplete(key: string): any[] | null {
    return this.get<any[]>(`autocomplete_${key}`);
  }
}

export const cacheService = new CacheService();