import { useState, useEffect, useCallback, useRef } from 'react';
import mapboxgl from 'mapbox-gl';

interface MapOptimizationOptions {
  maxZoom?: number;
  minZoom?: number;
  debounceTime?: number;
  enableClustering?: boolean;
  clusterRadius?: number;
}

interface OptimizedMapState {
  isMapLoaded: boolean;
  isMoving: boolean;
  viewport: {
    center: [number, number];
    zoom: number;
  };
}

export const useOptimizedMap = (options: MapOptimizationOptions = {}) => {
  const {
    maxZoom = 18,
    minZoom = 2,
    debounceTime = 300,
    enableClustering = false,
    clusterRadius = 50
  } = options;

  const [mapState, setMapState] = useState<OptimizedMapState>({
    isMapLoaded: false,
    isMoving: false,
    viewport: {
      center: [0, 0],
      zoom: 2
    }
  });

  const mapRef = useRef<mapboxgl.Map | null>(null);
  const moveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Manejar carga del mapa
  const handleMapLoad = useCallback(() => {
    setMapState(prev => ({
      ...prev,
      isMapLoaded: true
    }));
  }, []);

  // Manejar movimiento del mapa con debounce
  const handleMapMove = useCallback(() => {
    if (moveTimeoutRef.current) {
      clearTimeout(moveTimeoutRef.current);
    }

    setMapState(prev => ({
      ...prev,
      isMoving: true
    }));

    moveTimeoutRef.current = setTimeout(() => {
      if (mapRef.current) {
        const center = mapRef.current.getCenter();
        const zoom = mapRef.current.getZoom();
        
        setMapState(prev => ({
          ...prev,
          isMoving: false,
          viewport: {
            center: [center.lng, center.lat],
            zoom
          }
        }));
      }
    }, debounceTime);
  }, [debounceTime]);

  // Optimizar renderizado de marcadores
  const useMarkerOptimization = <T>(items: T[], getItemPosition: (item: T) => [number, number]) => {
    const [visibleItems, setVisibleItems] = useState<T[]>([]);
    
    useEffect(() => {
      if (!mapRef.current || !mapState.isMapLoaded) {
        setVisibleItems(items);
        return;
      }
      
      // Obtener bounds del mapa actual
      const bounds = mapRef.current.getBounds();
      
      // Filtrar items que están dentro de los bounds
      const filteredItems = items.filter(item => {
        const [lng, lat] = getItemPosition(item);
        return bounds.contains([lng, lat]);
      });
      
      setVisibleItems(filteredItems);
    }, [items, mapState.isMapLoaded, mapState.viewport]);
    
    return visibleItems;
  };

  // Configurar optimizaciones del mapa
  const setupMapOptimizations = useCallback((map: mapboxgl.Map) => {
    mapRef.current = map;
    
    // Configurar límites de zoom
    map.setMaxZoom(maxZoom);
    map.setMinZoom(minZoom);
    
    // Configurar eventos
    map.on('load', handleMapLoad);
    map.on('move', handleMapMove);
    map.on('zoom', handleMapMove);
    
    // Configurar clustering si está habilitado
    if (enableClustering) {
      // La implementación de clustering dependerá de los datos específicos
      console.log('Clustering enabled with radius:', clusterRadius);
    }
    
    return () => {
      map.off('load', handleMapLoad);
      map.off('move', handleMapMove);
      map.off('zoom', handleMapMove);
      
      if (moveTimeoutRef.current) {
        clearTimeout(moveTimeoutRef.current);
      }
    };
  }, [handleMapLoad, handleMapMove, maxZoom, minZoom, enableClustering, clusterRadius]);

  // Función para optimizar actualizaciones de capas
  const optimizeLayerUpdate = useCallback((
    layerId: string,
    data: any,
    updateFunction: (layerId: string, data: any) => void
  ) => {
    if (!mapState.isMoving) {
      updateFunction(layerId, data);
    }
  }, [mapState.isMoving]);

  return {
    mapState,
    setupMapOptimizations,
    useMarkerOptimization,
    optimizeLayerUpdate,
    mapRef
  };
};