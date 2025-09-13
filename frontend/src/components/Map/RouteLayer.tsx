import React, { useEffect, useMemo } from 'react';
import { Source, Layer, useMap } from 'react-map-gl';
import { RouteFeature, getRouteColor } from '../../types/map';

interface RouteLayerProps {
  routes: RouteFeature[];
  selectedRouteId?: string;
  onRouteClick?: (routeId: string) => void;
  showAllRoutes?: boolean;
}

function RouteLayer({
  routes,
  selectedRouteId,
  onRouteClick,
  showAllRoutes = true,
}: RouteLayerProps) {
  const { current: map } = useMap();

  // Filter routes to display
  const displayRoutes = useMemo(() => {
    if (showAllRoutes) {
      return routes;
    }
    return selectedRouteId 
      ? routes.filter(route => route.properties.route_id === selectedRouteId)
      : routes.slice(0, 1); // Show only the first route if none selected
  }, [routes, selectedRouteId, showAllRoutes]);

  // Create GeoJSON data for routes
  const routeGeoJSON = useMemo(() => ({
    type: 'FeatureCollection' as const,
    features: displayRoutes.map(route => ({
      ...route,
      properties: {
        ...route.properties,
        isSelected: route.properties.route_id === selectedRouteId,
        color: getRouteColor(
          route.properties.route_type,
          route.properties.route_id === selectedRouteId
        ),
        weight: route.properties.route_id === selectedRouteId ? 6 : 4,
        opacity: route.properties.route_id === selectedRouteId ? 1 : 0.7,
      },
    })),
  }), [displayRoutes, selectedRouteId]);

  // Handle route click
  useEffect(() => {
    if (!map || !onRouteClick) return;

    const handleClick = (e: any) => {
      const features = map.queryRenderedFeatures(e.point, {
        layers: ['route-line'],
      });

      if (features.length > 0) {
        const routeId = features[0].properties?.route_id;
        if (routeId) {
          onRouteClick(routeId);
        }
      }
    };

    map.on('click', 'route-line', handleClick);
    map.on('mouseenter', 'route-line', () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'route-line', () => {
      map.getCanvas().style.cursor = '';
    });

    return () => {
      map.off('click', 'route-line', handleClick);
      map.off('mouseenter', 'route-line');
      map.off('mouseleave', 'route-line');
    };
  }, [map, onRouteClick]);

  if (displayRoutes.length === 0) {
    return null;
  }

  return (
    <Source id="routes" type="geojson" data={routeGeoJSON}>
      {/* Route outline (for better visibility) */}
      <Layer
        id="route-outline"
        type="line"
        paint={{
          'line-color': '#ffffff',
          'line-width': [
            'case',
            ['get', 'isSelected'],
            8,
            6
          ],
          'line-opacity': 0.8,
        }}
        layout={{
          'line-join': 'round',
          'line-cap': 'round',
        }}
      />
      
      {/* Main route line */}
      <Layer
        id="route-line"
        type="line"
        paint={{
          'line-color': ['get', 'color'],
          'line-width': [
            'case',
            ['get', 'isSelected'],
            6,
            4
          ],
          'line-opacity': ['get', 'opacity'],
        }}
        layout={{
          'line-join': 'round',
          'line-cap': 'round',
        }}
      />
      
      {/* Route direction arrows (for selected route) */}
      <Layer
        id="route-arrows"
        type="symbol"
        filter={['==', ['get', 'isSelected'], true]}
        paint={{
          'icon-color': ['get', 'color'],
          'icon-opacity': 0.8,
        }}
        layout={{
          'symbol-placement': 'line',
          'symbol-spacing': 100,
          'icon-image': 'arrow-right',
          'icon-size': 0.8,
          'icon-rotation-alignment': 'map',
          'icon-pitch-alignment': 'map',
        }}
      />
    </Source>
  );
}

export default RouteLayer;