# Vehicle Data Validation

Este documento describe el sistema de validación de datos de vehículos implementado en la tarea 4.2.

## Características Implementadas

### 1. Validaciones de Patente (License Plate)
- **Formatos soportados**: 
  - Formato antiguo: `ABC123`
  - Formato nuevo: `AB123CD`
  - Formato alternativo: `123ABC`
- **Normalización**: Convierte a mayúsculas y elimina espacios
- **Validación**: Usa expresiones regulares para formatos argentinos

### 2. Validaciones de Consumo de Combustible
- **Rango válido**: 5.0 - 80.0 L/100km
- **Validación por tipo de vehículo**:
  - Auto: 5.0 - 15.0 L/100km
  - Camioneta: 8.0 - 20.0 L/100km
  - Camión: 15.0 - 50.0 L/100km
  - Colectivo: 20.0 - 80.0 L/100km
  - Motocicleta: 3.0 - 8.0 L/100km

### 3. Validaciones de Tipo de Combustible
- **Tipos soportados**:
  - `diesel_500`: Diesel común
  - `diesel_premium`: Diesel premium
  - `gasoline`: Nafta
- **Validación**: Verifica contra enum FuelType

### 4. Validaciones de Dimensiones
- **Altura**: 1.5 - 4.5 metros
- **Ancho**: 1.5 - 3.0 metros
- **Largo**: 3.0 - 25.0 metros
- **Validación cruzada**: Verifica proporciones lógicas

### 5. Validaciones de Peso
- **Peso vacío**: 500 - 50,000 kg
- **Peso máximo**: 500 - 50,000 kg
- **Validación cruzada**: Peso vacío < Peso máximo
- **Capacidad de carga**: Mínimo 10% del peso total

### 6. Validaciones de Año
- **Rango válido**: 1980 - 2030
- **Validación cruzada**: Vehículos nuevos con consumo alto generan advertencias

### 7. Validaciones de Modelo y Marca
- **Modelo**: Mínimo 2 caracteres, requerido
- **Marca**: Mínimo 2 caracteres, opcional
- **Normalización**: Elimina espacios extra

### 8. Validaciones de Notas
- **Longitud máxima**: 1000 caracteres
- **Normalización**: Elimina espacios extra

## Sistema de Advertencias de Compatibilidad

El sistema incluye un validador de compatibilidad que genera advertencias (no errores) para:

### Advertencias de Combustible
- Consumo alto para vehículos diesel (>40 L/100km)
- Consumo muy bajo para vehículos a nafta (<8 L/100km)

### Advertencias de Dimensiones
- Altura muy alta relativa al ancho (>2x)
- Largo menor que el ancho

### Advertencias de Peso
- Capacidad de carga muy baja (<10% del peso total)

### Advertencias de Año vs Consumo
- Consumo alto para vehículos relativamente nuevos (>2015 y >25 L/100km)

## Manejo de Errores

### Errores Individuales
Cada validación individual lanza `HTTPException` con código 400 y mensaje específico.

### Errores Múltiples
La validación completa acumula todos los errores y los devuelve en un formato estructurado:

```json
{
  "message": "Vehicle validation failed",
  "errors": [
    "License plate: Invalid Argentina license plate format",
    "Fuel consumption: Fuel consumption must be between 5.0 and 80.0 L/100km",
    "Dimensions: Vehicle height must be between 1.5 and 4.5 meters"
  ]
}
```

## Integración con Pydantic

Los schemas de Pydantic (`VehicleBase`, `VehicleCreate`, `VehicleUpdate`) utilizan los validadores para:
- Validación automática en la deserialización
- Normalización de datos
- Mensajes de error consistentes

## API Endpoints

### POST /vehicles/validate
Endpoint para validar datos de vehículos sin crear el vehículo:

```json
{
  "valid": true,
  "validated_data": { ... },
  "warnings": ["High fuel consumption for diesel vehicle"],
  "errors": []
}
```

## Uso en Servicios

El `VehicleService` utiliza las validaciones en:
- Creación de vehículos (`create_vehicle`)
- Actualización de vehículos (`update_vehicle`)
- Validación independiente (`validate_vehicle_data`)

## Tests

Los tests cubren:
- Validaciones individuales con casos válidos e inválidos
- Validación completa con datos parciales
- Sistema de advertencias de compatibilidad
- Manejo de errores múltiples

### Ejecutar Tests
```bash
cd backend
python test_validators_simple.py
```

## Beneficios

1. **Consistencia**: Validaciones uniformes en toda la aplicación
2. **Usabilidad**: Mensajes de error claros y específicos
3. **Flexibilidad**: Advertencias no bloquean la operación
4. **Mantenibilidad**: Validaciones centralizadas y reutilizables
5. **Robustez**: Manejo de errores múltiples y casos edge