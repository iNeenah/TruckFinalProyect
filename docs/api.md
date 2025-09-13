# Documentación de la API

## Autenticación

### POST /api/auth/login
Iniciar sesión con credenciales

**Request:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": "number",
  "user": {
    "id": "string",
    "email": "string",
    "full_name": "string",
    "role": "admin|operator",
    "company_id": "string|null",
    "is_active": "boolean",
    "created_at": "string",
    "last_login": "string"
  }
}
```

### POST /api/auth/register
Registrar un nuevo usuario

**Request:**
```json
{
  "email": "string",
  "password": "string",
  "full_name": "string",
  "company_name": "string (opcional)",
  "phone": "string (opcional)"
}
```

**Response:**
```json
{
  "id": "string",
  "email": "string",
  "full_name": "string",
  "role": "operator",
  "company_id": "string|null",
  "is_active": "boolean",
  "created_at": "string"
}
```

### POST /api/auth/logout
Cerrar sesión

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Vehículos

### GET /api/vehicles
Obtener todos los vehículos del usuario

**Response:**
```json
[
  {
    "id": "string",
    "license_plate": "string",
    "brand": "string",
    "model": "string",
    "year": "number",
    "fuel_type": "gasoline|diesel|electric",
    "fuel_efficiency": "number",
    "tank_capacity": "number",
    "weight": "number",
    "dimensions": {
      "length": "number",
      "width": "number",
      "height": "number"
    },
    "company_id": "string|null",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### GET /api/vehicles/{id}
Obtener un vehículo por ID

**Response:**
```json
{
  "id": "string",
  "license_plate": "string",
  "brand": "string",
  "model": "string",
  "year": "number",
  "fuel_type": "gasoline|diesel|electric",
  "fuel_efficiency": "number",
  "tank_capacity": "number",
  "weight": "number",
  "dimensions": {
    "length": "number",
    "width": "number",
    "height": "number"
  },
  "company_id": "string|null",
  "created_at": "string",
  "updated_at": "string"
}
```

### POST /api/vehicles
Crear un nuevo vehículo

**Request:**
```json
{
  "license_plate": "string",
  "brand": "string",
  "model": "string",
  "year": "number",
  "fuel_type": "gasoline|diesel|electric",
  "fuel_efficiency": "number",
  "tank_capacity": "number",
  "weight": "number",
  "dimensions": {
    "length": "number",
    "width": "number",
    "height": "number"
  }
}
```

**Response:**
```json
{
  "id": "string",
  "license_plate": "string",
  "brand": "string",
  "model": "string",
  "year": "number",
  "fuel_type": "gasoline|diesel|electric",
  "fuel_efficiency": "number",
  "tank_capacity": "number",
  "weight": "number",
  "dimensions": {
    "length": "number",
    "width": "number",
    "height": "number"
  },
  "company_id": "string|null",
  "created_at": "string",
  "updated_at": "string"
}
```

### PUT /api/vehicles/{id}
Actualizar un vehículo

**Request:**
```json
{
  "license_plate": "string",
  "brand": "string",
  "model": "string",
  "year": "number",
  "fuel_type": "gasoline|diesel|electric",
  "fuel_efficiency": "number",
  "tank_capacity": "number",
  "weight": "number",
  "dimensions": {
    "length": "number",
    "width": "number",
    "height": "number"
  }
}
```

**Response:**
```json
{
  "id": "string",
  "license_plate": "string",
  "brand": "string",
  "model": "string",
  "year": "number",
  "fuel_type": "gasoline|diesel|electric",
  "fuel_efficiency": "number",
  "tank_capacity": "number",
  "weight": "number",
  "dimensions": {
    "length": "number",
    "width": "number",
    "height": "number"
  },
  "company_id": "string|null",
  "created_at": "string",
  "updated_at": "string"
}
```

### DELETE /api/vehicles/{id}
Eliminar un vehículo

**Response:**
```json
{
  "message": "Vehicle deleted successfully"
}
```

## Rutas

### POST /api/routes/calculate
Calcular rutas entre dos puntos

**Request:**
```json
{
  "origin": "string",
  "destination": "string",
  "vehicle_id": "string"
}
```

**Response:**
```json
[
  {
    "id": "string",
    "origin": "string",
    "destination": "string",
    "distance": "number",
    "duration": "number",
    "fuel_cost": "number",
    "toll_cost": "number",
    "total_cost": "number",
    "savings": "number",
    "geometry": "array",
    "vehicle_id": "string",
    "created_at": "string"
  }
]
```

### GET /api/routes/saved
Obtener rutas guardadas del usuario

**Response:**
```json
[
  {
    "id": "string",
    "origin": "string",
    "destination": "string",
    "distance": "number",
    "duration": "number",
    "fuel_cost": "number",
    "toll_cost": "number",
    "total_cost": "number",
    "savings": "number",
    "geometry": "array",
    "vehicle_id": "string",
    "created_at": "string"
  }
]
```

### POST /api/routes/save
Guardar una ruta calculada

**Request:**
```json
{
  "origin": "string",
  "destination": "string",
  "distance": "number",
  "duration": "number",
  "fuel_cost": "number",
  "toll_cost": "number",
  "total_cost": "number",
  "savings": "number",
  "geometry": "array",
  "vehicle_id": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "origin": "string",
  "destination": "string",
  "distance": "number",
  "duration": "number",
  "fuel_cost": "number",
  "toll_cost": "number",
  "total_cost": "number",
  "savings": "number",
  "geometry": "array",
  "vehicle_id": "string",
  "created_at": "string"
}
```

### GET /api/routes/saved/{id}
Obtener una ruta guardada por ID

**Response:**
```json
{
  "id": "string",
  "origin": "string",
  "destination": "string",
  "distance": "number",
  "duration": "number",
  "fuel_cost": "number",
  "toll_cost": "number",
  "total_cost": "number",
  "savings": "number",
  "geometry": "array",
  "vehicle_id": "string",
  "created_at": "string"
}
```

### DELETE /api/routes/saved/{id}
Eliminar una ruta guardada

**Response:**
```json
{
  "message": "Route deleted successfully"
}
```

## Reportes

### GET /api/reports/statistics
Obtener estadísticas del usuario

**Response:**
```json
{
  "total_vehicles": "number",
  "total_routes": "number",
  "total_companies": "number",
  "total_users": "number",
  "routes_by_month": "array",
  "cost_analysis": {
    "total_fuel_cost": "number",
    "total_toll_cost": "number",
    "average_route_cost": "number"
  }
}
```

### POST /api/reports/generate
Generar un reporte

**Request:**
```json
{
  "type": "string",
  "start_date": "string (opcional)",
  "end_date": "string (opcional)",
  "vehicle_id": "string (opcional)"
}
```

**Response:**
```json
{
  "report_id": "string",
  "type": "string",
  "generated_at": "string",
  "data": "object"
}
```

## Administración (Solo para administradores)

### GET /api/admin/tolls
Obtener todos los peajes

**Response:**
```json
[
  {
    "id": "string",
    "name": "string",
    "latitude": "number",
    "longitude": "number",
    "cost": "number",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### POST /api/admin/tolls
Crear un nuevo peaje

**Request:**
```json
{
  "name": "string",
  "latitude": "number",
  "longitude": "number",
  "cost": "number"
}
```

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "latitude": "number",
  "longitude": "number",
  "cost": "number",
  "created_at": "string",
  "updated_at": "string"
}
```

### PUT /api/admin/tolls/{id}
Actualizar un peaje

**Request:**
```json
{
  "name": "string",
  "latitude": "number",
  "longitude": "number",
  "cost": "number"
}
```

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "latitude": "number",
  "longitude": "number",
  "cost": "number",
  "created_at": "string",
  "updated_at": "string"
}
```

### DELETE /api/admin/tolls/{id}
Eliminar un peaje

**Response:**
```json
{
  "message": "Toll deleted successfully"
}
```

### GET /api/admin/fuel-prices
Obtener precios de combustible

**Response:**
```json
[
  {
    "id": "string",
    "fuel_type": "gasoline|diesel",
    "price_per_liter": "number",
    "effective_date": "string",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### POST /api/admin/fuel-prices
Crear un nuevo precio de combustible

**Request:**
```json
{
  "fuel_type": "gasoline|diesel",
  "price_per_liter": "number",
  "effective_date": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "fuel_type": "gasoline|diesel",
  "price_per_liter": "number",
  "effective_date": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### PUT /api/admin/fuel-prices/{id}
Actualizar un precio de combustible

**Request:**
```json
{
  "fuel_type": "gasoline|diesel",
  "price_per_liter": "number",
  "effective_date": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "fuel_type": "gasoline|diesel",
  "price_per_liter": "number",
  "effective_date": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### DELETE /api/admin/fuel-prices/{id}
Eliminar un precio de combustible

**Response:**
```json
{
  "message": "Fuel price deleted successfully"
}
```

### GET /api/admin/users
Obtener todos los usuarios

**Response:**
```json
[
  {
    "id": "string",
    "email": "string",
    "full_name": "string",
    "role": "admin|operator",
    "company_id": "string|null",
    "is_active": "boolean",
    "created_at": "string",
    "last_login": "string"
  }
]
```

### PUT /api/admin/users/{id}
Actualizar un usuario

**Request:**
```json
{
  "email": "string",
  "full_name": "string",
  "role": "admin|operator",
  "is_active": "boolean"
}
```

**Response:**
```json
{
  "id": "string",
  "email": "string",
  "full_name": "string",
  "role": "admin|operator",
  "company_id": "string|null",
  "is_active": "boolean",
  "created_at": "string",
  "last_login": "string"
}
```

### DELETE /api/admin/users/{id}
Eliminar un usuario

**Response:**
```json
{
  "message": "User deleted successfully"
}
```