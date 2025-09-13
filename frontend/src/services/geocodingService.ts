import axios, { AxiosResponse } from 'axios';
import { GeocodingResponse, GeocodingResult, Location } from '../types/map';

class GeocodingService {
  private readonly mapboxToken: string;
  private readonly baseURL = 'https://api.mapbox.com/geocoding/v5/mapbox.places';

  constructor() {
    this.mapboxToken = process.env.VITE_MAPBOX_ACCESS_TOKEN || '';
  }

  /**
   * Search for places using Mapbox Geocoding API
   */
  async searchPlaces(
    query: string,
    options: {
      country?: string;
      bbox?: [number, number, number, number];
      proximity?: [number, number];
      types?: string[];
      limit?: number;
    } = {}
  ): Promise<GeocodingResult[]> {
    if (!this.mapboxToken) {
      throw new Error('Mapbox access token is required for geocoding');
    }

    if (!query.trim()) {
      return [];
    }

    try {
      const params = new URLSearchParams({
        access_token: this.mapboxToken,
        country: options.country || 'AR', // Default to Argentina
        limit: (options.limit || 5).toString(),
        language: 'es', // Spanish language
      });

      if (options.bbox) {
        params.append('bbox', options.bbox.join(','));
      }

      if (options.proximity) {
        params.append('proximity', options.proximity.join(','));
      }

      if (options.types && options.types.length > 0) {
        params.append('types', options.types.join(','));
      }

      const encodedQuery = encodeURIComponent(query);
      const url = `${this.baseURL}/${encodedQuery}.json?${params.toString()}`;

      const response: AxiosResponse<GeocodingResponse> = await axios.get(url);
      return response.data.features;
    } catch (error: any) {
      console.error('Geocoding error:', error);
      throw new Error('Failed to search places');
    }
  }

  /**
   * Reverse geocoding - get place information from coordinates
   */
  async reverseGeocode(
    coordinates: [number, number],
    options: {
      types?: string[];
      language?: string;
    } = {}
  ): Promise<GeocodingResult | null> {
    if (!this.mapboxToken) {
      throw new Error('Mapbox access token is required for geocoding');
    }

    try {
      const params = new URLSearchParams({
        access_token: this.mapboxToken,
        language: options.language || 'es',
      });

      if (options.types && options.types.length > 0) {
        params.append('types', options.types.join(','));
      }

      const [lng, lat] = coordinates;
      const url = `${this.baseURL}/${lng},${lat}.json?${params.toString()}`;

      const response: AxiosResponse<GeocodingResponse> = await axios.get(url);
      return response.data.features[0] || null;
    } catch (error: any) {
      console.error('Reverse geocoding error:', error);
      throw new Error('Failed to reverse geocode coordinates');
    }
  }

  /**
   * Search for addresses specifically
   */
  async searchAddresses(
    query: string,
    options: {
      country?: string;
      proximity?: [number, number];
      limit?: number;
    } = {}
  ): Promise<GeocodingResult[]> {
    return this.searchPlaces(query, {
      ...options,
      types: ['address', 'poi'],
    });
  }

  /**
   * Search for cities and places
   */
  async searchCities(
    query: string,
    options: {
      country?: string;
      limit?: number;
    } = {}
  ): Promise<GeocodingResult[]> {
    return this.searchPlaces(query, {
      ...options,
      types: ['place', 'locality', 'neighborhood'],
    });
  }

  /**
   * Search for points of interest
   */
  async searchPOIs(
    query: string,
    options: {
      country?: string;
      proximity?: [number, number];
      limit?: number;
    } = {}
  ): Promise<GeocodingResult[]> {
    return this.searchPlaces(query, {
      ...options,
      types: ['poi'],
    });
  }

  /**
   * Convert GeocodingResult to Location
   */
  geocodingResultToLocation(result: GeocodingResult): Location {
    return {
      name: this.extractLocationName(result),
      address: result.place_name,
      coordinates: result.center,
      metadata: {
        id: result.id,
        place_type: result.place_type,
        relevance: result.relevance,
        properties: result.properties,
        context: result.context,
      },
    };
  }

  /**
   * Extract a clean location name from geocoding result
   */
  private extractLocationName(result: GeocodingResult): string {
    // Try to get the most specific name
    const parts = result.place_name.split(',');
    
    // For POIs, use the first part
    if (result.place_type.includes('poi')) {
      return parts[0].trim();
    }
    
    // For addresses, use the first part (street address)
    if (result.place_type.includes('address')) {
      return parts[0].trim();
    }
    
    // For places, use the first part (city/locality name)
    if (result.place_type.includes('place') || result.place_type.includes('locality')) {
      return parts[0].trim();
    }
    
    // Default to first part
    return parts[0].trim();
  }

  /**
   * Get suggestions for autocomplete
   */
  async getAutocompleteSuggestions(
    query: string,
    options: {
      proximity?: [number, number];
      limit?: number;
    } = {}
  ): Promise<Location[]> {
    if (query.length < 2) {
      return [];
    }

    try {
      const results = await this.searchPlaces(query, {
        country: 'AR',
        limit: options.limit || 5,
        proximity: options.proximity,
        types: ['address', 'poi', 'place', 'locality'],
      });

      return results.map(result => this.geocodingResultToLocation(result));
    } catch (error) {
      console.error('Autocomplete error:', error);
      return [];
    }
  }

  /**
   * Validate coordinates are within Argentina bounds
   */
  isWithinArgentina(coordinates: [number, number]): boolean {
    const [lng, lat] = coordinates;
    
    // Rough bounds for Argentina
    const argBounds = {
      west: -73.5,
      east: -53.6,
      south: -55.0,
      north: -21.8,
    };
    
    return (
      lng >= argBounds.west &&
      lng <= argBounds.east &&
      lat >= argBounds.south &&
      lat <= argBounds.north
    );
  }

  /**
   * Validate coordinates are within Misiones province
   */
  isWithinMisiones(coordinates: [number, number]): boolean {
    const [lng, lat] = coordinates;
    
    // Rough bounds for Misiones province
    const misionesBounds = {
      west: -56.5,
      east: -53.6,
      south: -28.2,
      north: -25.2,
    };
    
    return (
      lng >= misionesBounds.west &&
      lng <= misionesBounds.east &&
      lat >= misionesBounds.south &&
      lat <= misionesBounds.north
    );
  }

  /**
   * Format address for display
   */
  formatAddress(result: GeocodingResult): string {
    const parts = result.place_name.split(',');
    
    // Remove country (usually the last part)
    if (parts.length > 1 && parts[parts.length - 1].trim().toLowerCase() === 'argentina') {
      parts.pop();
    }
    
    return parts.join(',').trim();
  }

  /**
   * Get place context (city, province, etc.)
   */
  getPlaceContext(result: GeocodingResult): {
    city?: string;
    province?: string;
    country?: string;
  } {
    const context: { city?: string; province?: string; country?: string } = {};
    
    if (result.context) {
      result.context.forEach(item => {
        if (item.id.startsWith('place.')) {
          context.city = item.text;
        } else if (item.id.startsWith('region.')) {
          context.province = item.text;
        } else if (item.id.startsWith('country.')) {
          context.country = item.text;
        }
      });
    }
    
    return context;
  }
}

// Create and export singleton instance
export const geocodingService = new GeocodingService();