# OSRM Integration

Este documento describe la integración con OSRM (Open Source Routing Machine) para el cálculo de rutas en el optimizador de rutas.

## Características Implementadas

### 1. Servicio OSRM (OSRMService)

Servicio principal para interactuar con la API de OSRM:

- **Cálculo de rutas**: Rutas entre múltiples puntos con alternativas
- **Matriz de distancias**: Cálculo de matrices de distancia/tiempo
- **Búsqueda de puntos cercanos**: Encontrar segmentos de carretera más cercanos
- **Map matching**: Ajustar coordenadas GPS a la red de carreteras
- **Health check**: Verificar estado del servicio OSRM

### 2. Modelos de Datos

#### Coordinate
```python
@dataclass
class Coordinate:
    longitude: float
    latitude: float
    
    def to_osrm_format(self) -> str:
        return f"{self.longitude},{self.latitude}"
```

#### Route, RouteLeg, RouteStep
Estructuras jerárquicas para representar rutas completas con instrucciones paso a paso.

#### OSRMResponse
Respuesta estructurada de la API OSRM con rutas y waypoints.

### 3. Perfiles de Enrutamiento

- **DRIVING**: Vehículos (por defecto)
- **WALKING**: Peatones
- **CYCLING**: Bicicletas

### 4. Formatos de Geometría

- **GEOJSON**: Formato GeoJSON (recomendado)
- **POLYLINE**: Polyline comprimido
- **POLYLINE6**: Polyline con 6 decimales de precisión

## Configuración

### Variables de Entorno

```bash
# URL del servicio OSRM
OSRM_URL=http://localhost:5000

# Opcional: Tokens para geocodificación
MAPBOX_ACCESS_TOKEN=your_mapbox_token
GOOGLE_MAPS_API_KEY=your_google_api_key
```

### Docker Compose

El servicio OSRM está configurado en `docker-compose.yml`:

```yaml
osrm:
  image: osrm/osrm-backend:latest
  container_name: optimizador_osrm
  ports:
    - "5000:5000"
  volumes:
    - ./osrm-data:/data
  command: osrm-routed --algorithm mld /data/argentina-latest.osrm
```

## Preparación de Datos

### Descarga y Preparación Automática

**Linux/Mac:**
```bash
chmod +x scripts/setup_osrm_data.sh
./scripts/setup_osrm_data.sh
```

**Windows:**
```powershell
.\scripts\setup_osrm_data.ps1
```

### Preparación Manual

1. **Descargar datos de Argentina:**
```bash
mkdir osrm-data
cd osrm-data
wget https://download.geofabrik.de/south-america/argentina-latest.osm.pbf
```

2. **Procesar datos con OSRM:**
```bash
# Extraer
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/argentina-latest.osm.pbf

# Particionar
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/argentina-latest.osrm

# Personalizar
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/argentina-latest.osrm
```

3. **Iniciar servicio:**
```bash
docker-compose up osrm
```

## Uso del Servicio

### Ejemplo Básico

```python
from app.services.osrm_service import OSRMService, Coordinate

async def calculate_route():
    async with OSRMService() as osrm:
        # Coordenadas de ejemplo (Posadas a Puerto Iguazú)
        origin = Coordinate(-55.8959, -27.3621)
        destination = Coordinate(-54.5735, -25.5951)
        
        # Calcular ruta
        response = await osrm.route([origin, destination])
        
        if response.routes:
            route = response.routes[0]
            print(f"Distancia: {route.distance/1000:.1f} km")
            print(f"Tiempo: {route.duration/60:.1f} minutos")
```

### Rutas con Alternativas

```python
async def get_alternatives():
    async with OSRMService() as osrm:
        origin = Coordinate(-55.8959, -27.3621)
        destination = Coordinate(-54.5735, -25.5951)
        
        routes = await osrm.get_route_alternatives(
            origin, destination, max_alternatives=3
        )
        
        for i, route in enumerate(routes):
            print(f"Ruta {i+1}: {route.distance/1000:.1f} km, {route.duration/60:.1f} min")
```

### Matriz de Distancias

```python
async def calculate_matrix():
    async with OSRMService() as osrm:
        origins = [Coordinate(-55.8959, -27.3621)]  # Posadas
        destinations = [
            Coordinate(-54.5735, -25.5951),  # Puerto Iguazú
            Coordinate(-55.5377, -27.3671)   # Oberá
        ]
        
        matrix = await osrm.calculate_route_matrix(origins, destinations)
        
        durations = matrix["durations"][0]  # Primera fila (desde Posadas)
        for i, duration in enumerate(durations):
            print(f"Tiempo a destino {i+1}: {duration/60:.1f} minutos")
```

## Validación de Coordenadas

### Funciones de Validación de Límites

```python
from app.services.osrm_service import argentina_bounds_check, misiones_bounds_check

# Verificar si está en Argentina
coord = Coordinate(-58.3816, -34.6037)  # Buenos Aires
if argentina_bounds_check(coord):
    print("Coordenada válida para Argentina")

# Verificar si está en Misiones
coord = Coordinate(-55.8959, -27.3621)  # Posadas
if misiones_bounds_check(coord):
    print("Coordenada válida para Misiones")
```

## Integración con Geocodificación

El servicio se integra con el `GeocodingService` para convertir direcciones en coordenadas:

```python
from app.services.geocoding_service import GeocodingService
from app.services.osrm_service import OSRMService

async def route_from_addresses():
    async with GeocodingService() as geocoder:
        async with OSRMService() as osrm:
            # Geocodificar direcciones
            origin_results = await geocoder.geocode_misiones_address(
                "Av. Mitre 123, Posadas"
            )
            dest_results = await geocoder.geocode_misiones_address(
                "Av. Victoria Aguirre 456, Puerto Iguazú"
            )
            
            if origin_results and dest_results:
                # Calcular ruta
                response = await osrm.route([
                    origin_results[0].coordinate,
                    dest_results[0].coordinate
                ])
                
                return response.routes[0] if response.routes else None
```

## Manejo de Errores

### Errores Comunes

1. **Servicio no disponible**: `OSRMService.health_check()` retorna `False`
2. **Sin ruta encontrada**: OSRM retorna código "NoRoute"
3. **Coordenadas inválidas**: Fuera de los límites de Argentina
4. **Timeout**: Requests que tardan más de 30 segundos

### Ejemplo de Manejo de Errores

```python
async def safe_route_calculation(origin, destination):
    async with OSRMService() as osrm:
        try:
            # Verificar salud del servicio
            if not await osrm.health_check():
                raise Exception("OSRM service not available")
            
            # Validar coordenadas
            if not argentina_bounds_check(origin):
                raise ValueError("Origin outside Argentina bounds")
            
            if not argentina_bounds_check(destination):
                raise ValueError("Destination outside Argentina bounds")
            
            # Calcular ruta
            response = await osrm.route([origin, destination])
            
            if not response.routes:
                raise Exception("No route found")
            
            return response.routes[0]
            
        except httpx.TimeoutException:
            raise Exception("Route calculation timed out")
        except httpx.HTTPError as e:
            raise Exception(f"OSRM request failed: {e}")
```

## Testing

### Tests Unitarios

```bash
cd backend
python -m pytest tests/test_osrm_service.py -v
```

### Tests de Integración

Los tests de integración requieren un servicio OSRM ejecutándose:

```bash
# Iniciar OSRM
docker-compose up -d osrm

# Ejecutar tests de integración
python -m pytest tests/test_osrm_service.py -v -m integration
```

## Optimizaciones

### 1. Caché de Rutas

Implementar caché Redis para rutas frecuentemente calculadas:

```python
import redis
import json
import hashlib

class CachedOSRMService(OSRMService):
    def __init__(self, redis_client=None):
        super().__init__()
        self.redis = redis_client or redis.Redis.from_url(settings.redis_url)
    
    async def route(self, coordinates, **kwargs):
        # Crear clave de caché
        cache_key = self._create_cache_key(coordinates, kwargs)
        
        # Buscar en caché
        cached = self.redis.get(cache_key)
        if cached:
            return OSRMResponse(**json.loads(cached))
        
        # Calcular y cachear
        response = await super().route(coordinates, **kwargs)
        self.redis.setex(
            cache_key, 
            3600,  # 1 hora
            json.dumps(response.__dict__)
        )
        
        return response
```

### 2. Pool de Conexiones

Para aplicaciones de alto tráfico, usar pool de conexiones HTTP.

### 3. Retry Logic

Implementar reintentos automáticos para requests fallidos.

## Limitaciones

1. **Datos de Argentina**: Solo incluye carreteras de Argentina
2. **Actualizaciones**: Los datos OSM deben actualizarse manualmente
3. **Memoria**: OSRM requiere ~8GB RAM para datos de Argentina
4. **Tiempo de inicio**: La preparación inicial de datos toma ~30 minutos

## Próximos Pasos

1. Implementar caché Redis para optimizar performance
2. Agregar soporte para restricciones de vehículos (altura, peso)
3. Integrar datos de tráfico en tiempo real
4. Implementar geocodificación offline para direcciones argentinas
5. Agregar soporte para waypoints intermedios en rutas