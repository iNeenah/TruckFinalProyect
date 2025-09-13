# Manual de Usuario - Optimizador de Rutas con IA

## Índice
1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Primeros Pasos](#primeros-pasos)
5. [Gestión de Vehículos](#gestión-de-vehículos)
6. [Cálculo de Rutas](#cálculo-de-rutas)
7. [Visualización de Rutas](#visualización-de-rutas)
8. [Guardado de Rutas](#guardado-de-rutas)
9. [Reportes y Estadísticas](#reportes-y-estadísticas)
10. [Panel de Administración](#panel-de-administración)
11. [Configuración](#configuración)
12. [Solución de Problemas](#solución-de-problemas)

## Introducción

El Optimizador de Rutas con IA es una aplicación web que permite calcular rutas óptimas para vehículos comerciales considerando costos de combustible y peajes. La aplicación ayuda a las empresas de transporte a reducir costos y mejorar la eficiencia operativa.

## Requisitos del Sistema

### Requisitos Mínimos
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexión a internet estable
- Resolución mínima de 1024x768

### Requisitos Recomendados
- Navegador web actualizado
- Conexión a internet de alta velocidad
- Resolución de 1920x1080 o superior

## Instalación

### Para Usuarios Finales
1. Acceder a la URL proporcionada por el administrador del sistema
2. Iniciar sesión con las credenciales proporcionadas

### Para Administradores del Sistema
1. Clonar el repositorio del proyecto
2. Configurar las variables de entorno
3. Ejecutar `docker-compose up` para iniciar todos los servicios
4. Acceder a la aplicación en `http://localhost:3000`

## Primeros Pasos

### Inicio de Sesión
1. Abrir el navegador y acceder a la URL de la aplicación
2. Ingresar el correo electrónico y contraseña proporcionados
3. Hacer clic en "Iniciar Sesión"

### Registro de Nuevos Usuarios
1. Hacer clic en "Registrarse" en la página de inicio de sesión
2. Completar el formulario con:
   - Correo electrónico
   - Nombre completo
   - Contraseña (mínimo 8 caracteres)
   - Confirmar contraseña
3. Hacer clic en "Registrarse"

### Pantalla Principal (Dashboard)
Después de iniciar sesión, se mostrará el dashboard con:
- Resumen de estadísticas
- Accesos rápidos a las principales funciones
- Últimas rutas guardadas

## Gestión de Vehículos

### Ver Lista de Vehículos
1. Hacer clic en "Vehículos" en el menú lateral
2. Se mostrará una tabla con todos los vehículos registrados

### Agregar Nuevo Vehículo
1. En la página de vehículos, hacer clic en "Nuevo Vehículo"
2. Completar el formulario con:
   - Patente
   - Marca
   - Modelo
   - Año
   - Tipo de combustible
   - Eficiencia de combustible (km/litro)
   - Capacidad del tanque (litros)
   - Peso (kg)
   - Dimensiones (largo, ancho, alto)
3. Hacer clic en "Guardar"

### Editar Vehículo
1. En la lista de vehículos, hacer clic en el botón "Editar" del vehículo deseado
2. Modificar los campos necesarios
3. Hacer clic en "Guardar"

### Eliminar Vehículo
1. En la lista de vehículos, hacer clic en el botón "Eliminar" del vehículo deseado
2. Confirmar la eliminación en el diálogo que aparece

### Filtrar Vehículos
1. Utilizar el panel de filtros en la parte superior de la lista
2. Ingresar criterios de búsqueda como marca, modelo o patente
3. Los resultados se actualizarán automáticamente

## Cálculo de Rutas

### Acceder al Calculador de Rutas
1. Hacer clic en "Rutas" en el menú lateral
2. Se mostrará el formulario de cálculo de rutas

### Calcular una Ruta
1. Ingresar el punto de origen en el campo correspondiente
2. Ingresar el punto de destino en el campo correspondiente
3. Seleccionar un vehículo de la lista desplegable
4. Hacer clic en "Calcular Rutas"

### Características del Cálculo
- El sistema calcula múltiples alternativas de ruta
- Cada ruta muestra:
  - Distancia total
  - Tiempo estimado
  - Costo de combustible
  - Costo de peajes
  - Costo total
  - Ahorro potencial respecto a otras rutas

## Visualización de Rutas

### Ver Rutas en el Mapa
1. Después de calcular rutas, se mostrarán en una lista
2. Hacer clic en "Ver en Mapa" para visualizar una ruta específica
3. Las rutas se muestran con diferentes colores para fácil identificación

### Comparar Rutas
1. Todas las rutas calculadas se muestran en una tabla comparativa
2. Se puede seleccionar una ruta haciendo clic en "Seleccionar"
3. La ruta seleccionada se resalta en el mapa

### Detalles de Ruta
1. Hacer clic en una ruta para ver detalles adicionales
2. Se muestra información detallada de costos y tiempo

## Guardado de Rutas

### Guardar una Ruta
1. Después de calcular una ruta, hacer clic en "Guardar" en la ruta deseada
2. La ruta se almacenará en el historial de rutas guardadas

### Ver Rutas Guardadas
1. Las rutas guardadas se muestran en:
   - El dashboard (últimas rutas)
   - La sección de Reportes
2. Se pueden reutilizar o eliminar según sea necesario

### Eliminar Ruta Guardada
1. En la lista de rutas guardadas, hacer clic en "Eliminar"
2. Confirmar la eliminación

## Reportes y Estadísticas

### Acceder a Reportes
1. Hacer clic en "Reportes" en el menú lateral
2. Se mostrará el panel de reportes

### Tipos de Reportes
- Estadísticas generales de uso
- Análisis de costos por vehículo
- Historial de rutas calculadas
- Comparativa de eficiencia

### Exportar Reportes
1. En la página de reportes, hacer clic en "Exportar a PDF"
2. Se generará y descargará un reporte en formato PDF

### Visualización de Datos
- Gráficos interactivos de estadísticas
- Tablas con datos detallados
- Filtros por período y vehículo

## Panel de Administración

### Acceso al Panel
1. Solo usuarios con rol de "Administrador" pueden acceder
2. Hacer clic en "Administración" en el menú lateral

### Gestión de Peajes
1. Agregar, editar o eliminar peajes
2. Cada peaje incluye:
   - Nombre
   - Ubicación (latitud/longitud)
   - Costo

### Gestión de Precios de Combustible
1. Configurar precios actuales de combustible
2. Los precios se utilizan para calcular costos de rutas

### Gestión de Usuarios
1. Ver lista de todos los usuarios registrados
2. Editar roles y permisos de usuarios
3. Activar o desactivar cuentas de usuario

## Configuración

### Preferencias de Usuario
1. Hacer clic en el avatar del usuario en la barra superior
2. Seleccionar "Configuración"
3. Opciones disponibles:
   - Cambiar tema (claro/oscuro)
   - Cambiar contraseña
   - Configurar notificaciones

### Configuración del Sistema
1. Solo disponible para administradores
2. Incluye:
   - Configuración de correo electrónico
   - Parámetros de cálculo
   - Configuración de seguridad

## Solución de Problemas

### Problemas Comunes

#### No se pueden calcular rutas
- Verificar conexión a internet
- Asegurarse de que se haya seleccionado un vehículo
- Verificar que los puntos de origen y destino sean válidos

#### Las rutas no se muestran en el mapa
- Verificar que el navegador permita mostrar mapas
- Recargar la página
- Verificar que JavaScript esté habilitado

#### Error al iniciar sesión
- Verificar que el correo y contraseña sean correctos
- Asegurarse de que la cuenta esté activa
- Contactar al administrador si el problema persiste

#### La aplicación funciona lentamente
- Verificar la velocidad de la conexión a internet
- Cerrar otras pestañas o aplicaciones
- Limpiar la caché del navegador

### Contacto de Soporte
Para problemas que no se resuelven con esta guía:
- Email: soporte@kiro.com
- Teléfono: +54 11 1234-5678
- Horario: Lunes a Viernes, 9:00 a 18:00

## Avisos Legales

### Privacidad
La aplicación cumple con las normativas de protección de datos. Toda la información se almacena de forma segura y solo se utiliza para los fines del servicio.

### Términos de Uso
Al utilizar esta aplicación, acepta los términos y condiciones establecidos por el proveedor del servicio.

### Actualizaciones
La aplicación se actualiza regularmente para mejorar la seguridad y funcionalidad. Se recomienda mantenerse actualizado con las últimas versiones.