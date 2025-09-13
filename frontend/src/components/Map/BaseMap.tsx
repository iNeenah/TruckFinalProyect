import React, { useRef, useEffect, useState, useCallback } from 'react';
import Map, { 
  MapRef, 
  NavigationControl, 
  FullscreenControl, 
  ScaleControl, 
  GeolocateControl,
  MapboxEvent,
  ViewStateChangeEvent
} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import {
  MapConfig,
  MapClickEvent,
  MapMoveEvent,
  MapControl,
  MapStyle,
  DEFAULT_MAP_CONFIG,
  MAP_STYLES,
} from '../../types/map';
import { useTheme } from '../../contexts/ThemeContext';

interface BaseMapProps {
  config?: Partial<MapConfig>;
  controls?: MapControl[];
  onClick?: (event: MapClickEvent) => void;
  onMove?: (event: MapMoveEvent) => void;
  onLoad?: () => void;
  className?: string;
  children?: React.ReactNode;
}

function BaseMap({
  config = {},
  controls = ['navigation', 'fullscreen', 'scale'],
  onClick,
  onMove,
  onLoad,
  className = 'w-full h-full',
  children,
}: BaseMapProps) {
  const mapRef = useRef<MapRef>(null);
  const { actualTheme } = useTheme();
  const [isLoaded, setIsLoaded] = useState(false);
  const [viewState, setViewState] = useState({
    longitude: config.center?.[0] || DEFAULT_MAP_CONFIG.center[0],
    latitude: config.center?.[1] || DEFAULT_MAP_CONFIG.center[1],
    zoom: config.zoom || DEFAULT_MAP_CONFIG.zoom,
  });

  const mapConfig = {
    ...DEFAULT_MAP_CONFIG,
    ...config,
  };

  // Adjust map style based on theme
  const getMapStyle = useCallback((): MapStyle => {
    if (config.style) {
      return config.style;
    }
    
    return actualTheme === 'dark' 
      ? MAP_STYLES.DARK 
      : MAP_STYLES.STREETS;
  }, [actualTheme, config.style]);

  const handleMapClick = useCallback((event: MapboxEvent) => {
    if (!onClick) return;
    
    const { lngLat, point } = event;
    const features = mapRef.current?.queryRenderedFeatures(point);
    
    onClick({
      lngLat: [lngLat.lng, lngLat.lat],
      point: [point.x, point.y],
      features,
    });
  }, [onClick]);

  const handleMapMove = useCallback((event: ViewStateChangeEvent) => {
    const { viewState: newViewState } = event;
    setViewState(newViewState);
    
    if (!onMove) return;
    
    const map = mapRef.current;
    if (!map) return;
    
    onMove({
      center: [newViewState.longitude, newViewState.latitude],
      zoom: newViewState.zoom,
      bounds: map.getBounds(),
    });
  }, [onMove]);

  const handleMapLoad = useCallback(() => {
    setIsLoaded(true);
    onLoad?.();
  }, [onLoad]);

  // Public methods for parent components
  const fitBounds = useCallback((bounds: any, options?: any) => {
    mapRef.current?.fitBounds(bounds, {
      padding: 50,
      duration: 1000,
      ...options,
    });
  }, []);

  const flyTo = useCallback((coordinates: [number, number], zoom?: number) => {
    mapRef.current?.flyTo({
      center: coordinates,
      zoom: zoom || viewState.zoom,
      duration: 1000,
    });
  }, [viewState.zoom]);

  const getMap = useCallback(() => mapRef.current, []);

  // Expose methods to parent via ref
  React.useImperativeHandle(mapRef, () => ({
    ...mapRef.current,
    fitBounds,
    flyTo,
    getMap,
  }));

  // Check if Mapbox token is available
  if (!mapConfig.accessToken) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-100 dark:bg-gray-800`}>
        <div className="text-center p-8">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900 mb-4">
            <svg className="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Mapbox Token Required
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Please configure your Mapbox access token in the environment variables.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <Map
        ref={mapRef}
        {...viewState}
        onMove={handleMapMove}
        onClick={handleMapClick}
        onLoad={handleMapLoad}
        mapboxAccessToken={mapConfig.accessToken}
        mapStyle={getMapStyle()}
        maxBounds={mapConfig.maxBounds}
        attributionControl={false}
        logoPosition="bottom-left"
        style={{ width: '100%', height: '100%' }}
      >
        {/* Navigation Control */}
        {controls.includes('navigation') && (
          <NavigationControl 
            position="top-right" 
            showCompass={true}
            showZoom={true}
          />
        )}

        {/* Fullscreen Control */}
        {controls.includes('fullscreen') && (
          <FullscreenControl position="top-right" />
        )}

        {/* Scale Control */}
        {controls.includes('scale') && (
          <ScaleControl 
            position="bottom-left"
            maxWidth={100}
            unit="metric"
          />
        )}

        {/* Geolocate Control */}
        {controls.includes('geolocate') && (
          <GeolocateControl
            position="top-right"
            trackUserLocation={true}
            showUserHeading={true}
          />
        )}

        {/* Custom children components */}
        {isLoaded && children}
      </Map>
    </div>
  );
}

export default BaseMap;
export type { BaseMapProps };