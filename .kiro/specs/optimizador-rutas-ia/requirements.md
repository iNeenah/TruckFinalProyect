# Requirements Document

## Introduction

El Optimizador de Rutas con IA es un Software como Servicio (SaaS) web diseñado para empresas de transporte de Misiones que buscan reducir costos operativos mediante la optimización inteligente de rutas. La plataforma calcula no solo la ruta más rápida, sino la más económica, considerando costos de combustible y peajes para generar ahorros tangibles y recopilar datos valiosos del sector.

La propuesta de valor central es: "Te mostramos la ruta más barata, no solo la más rápida, para tus viajes. Ahorra en combustible y peajes".

## Requirements

### Requirement 1: Gestión de Usuarios y Empresas

**User Story:** Como dueño de una empresa de transporte, quiero registrarme y gestionar mi cuenta en la plataforma, para que pueda acceder a las funcionalidades de optimización de rutas de forma segura.

#### Acceptance Criteria

1. WHEN un usuario accede a la plataforma THEN el sistema SHALL mostrar opciones de registro y login
2. WHEN un usuario se registra THEN el sistema SHALL crear una cuenta asociada a su empresa
3. WHEN un usuario inicia sesión THEN el sistema SHALL autenticar las credenciales y proporcionar acceso a su dashboard
4. IF un usuario no está autenticado THEN el sistema SHALL restringir el acceso a las funcionalidades principales
5. WHEN un usuario cierra sesión THEN el sistema SHALL invalidar la sesión activa

### Requirement 2: Gestión de Flota de Vehículos

**User Story:** Como jefe de logística, quiero registrar y gestionar los datos completos de mis camiones, para que el sistema pueda calcular costos precisos y considerar restricciones operativas de cada vehículo.

#### Acceptance Criteria

1. WHEN un usuario accede a la gestión de flota THEN el sistema SHALL mostrar una lista de vehículos registrados
2. WHEN un usuario registra un nuevo camión THEN el sistema SHALL requerir: patente, modelo, consumo promedio (L/100km), tipo de combustible (Diesel 500/Premium), dimensiones (alto, ancho) y peso máximo
3. WHEN un usuario edita datos de un camión THEN el sistema SHALL actualizar la información y validar los datos ingresados
4. WHEN un usuario elimina un camión THEN el sistema SHALL confirmar la acción y remover el vehículo de la flota
5. IF los datos de consumo o dimensiones son inválidos THEN el sistema SHALL mostrar un mensaje de error específico
6. WHEN se selecciona tipo de combustible THEN el sistema SHALL aplicar el precio correspondiente en los cálculos de costo

### Requirement 3: Cálculo y Optimización de Rutas

**User Story:** Como operador logístico, quiero calcular la ruta más económica entre dos puntos usando un vehículo específico, para que pueda tomar decisiones informadas que reduzcan los costos operativos en las rutas principales de Misiones.

#### Acceptance Criteria

1. WHEN un usuario ingresa origen, destino y selecciona un camión THEN el sistema SHALL calcular múltiples opciones de ruta considerando las rutas principales (RN12, RN14) que conectan Misiones con centros logísticos
2. WHEN el sistema calcula rutas THEN SHALL evaluar costos de combustible basados en distancia, consumo del vehículo y tipo de combustible específico
3. WHEN el sistema evalúa rutas THEN SHALL identificar y calcular costos de peajes en cada alternativa usando tarifas actualizadas
4. WHEN el cálculo está completo THEN el sistema SHALL recomendar la ruta con menor costo total
5. WHEN se muestra la ruta recomendada THEN el sistema SHALL desglosar costos: combustible, peajes y total
6. IF no se puede calcular una ruta THEN el sistema SHALL mostrar un mensaje de error explicativo
7. WHEN se calculan rutas THEN el sistema SHALL considerar restricciones de dimensiones y peso del vehículo para rutas futuras

### Requirement 4: Visualización de Rutas y Mapas

**User Story:** Como usuario de la plataforma, quiero ver las rutas calculadas en un mapa interactivo con información detallada, para que pueda entender visualmente las opciones y tomar decisiones informadas.

#### Acceptance Criteria

1. WHEN se calcula una ruta THEN el sistema SHALL mostrar la ruta en un mapa interactivo
2. WHEN se muestra el mapa THEN el sistema SHALL destacar la ruta recomendada visualmente
3. WHEN hay múltiples opciones THEN el sistema SHALL permitir comparar rutas alternativas
4. WHEN se selecciona una ruta THEN el sistema SHALL mostrar información detallada: distancia, tiempo estimado y costos
5. WHEN se visualiza una ruta THEN el sistema SHALL marcar ubicaciones de peajes identificados

### Requirement 5: Comparación y Análisis de Ahorro

**User Story:** Como empresario del transporte, quiero ver claramente cuánto dinero ahorro con la ruta optimizada comparada con alternativas, para que pueda justificar el uso de la plataforma y medir su valor.

#### Acceptance Criteria

1. WHEN el sistema calcula rutas THEN SHALL comparar la ruta recomendada con la ruta más rápida tradicional
2. WHEN se muestra la comparación THEN el sistema SHALL indicar el ahorro en pesos argentinos
3. WHEN se presenta el ahorro THEN el sistema SHALL desglosar la diferencia por combustible y peajes
4. WHEN no hay ahorro significativo THEN el sistema SHALL informar que la ruta rápida es también la más económica
5. IF hay múltiples alternativas rentables THEN el sistema SHALL mostrar un ranking de opciones por ahorro

### Requirement 6: Gestión de Datos de Costos

**User Story:** Como administrador del sistema, quiero gestionar manualmente los datos de precios de combustible y peajes a través de una interfaz administrativa, para que los cálculos de costos sean precisos y actualizados según las condiciones del mercado regional.

#### Acceptance Criteria

1. WHEN un administrador accede al panel administrativo THEN el sistema SHALL mostrar opciones para actualizar precios de combustible (Diesel 500, Diesel Premium) y tarifas de peajes
2. WHEN se actualizan precios de combustible THEN el sistema SHALL permitir ingresar precios diferenciados por tipo y región (NEA)
3. WHEN se gestionan peajes THEN el sistema SHALL permitir actualizar tarifas para cada punto de peaje en rutas principales (RN12, RN14)
4. WHEN los datos de precios tienen más de 30 días THEN el sistema SHALL mostrar una alerta de "datos desactualizados" a los usuarios
5. IF no hay datos de precios disponibles THEN el sistema SHALL usar valores por defecto predefinidos y notificar claramente al usuario
6. WHEN se actualizan precios THEN el sistema SHALL aplicar los nuevos valores a cálculos futuros inmediatamente
7. WHEN se modifican datos de costos THEN el sistema SHALL registrar fecha y usuario responsable de la actualización

### Requirement 7: Panel de Administración del Sistema

**User Story:** Como administrador del sistema, quiero acceder a un panel de administración completo, para que pueda gestionar usuarios, actualizar datos críticos del sistema y mantener la plataforma operativa.

#### Acceptance Criteria

1. WHEN un usuario con rol 'Admin' inicia sesión THEN el sistema SHALL mostrar acceso al panel de administración
2. WHEN se accede al panel administrativo THEN SHALL permitir gestionar: precios de combustible por tipo y región, tarifas de peajes por ubicación, y datos de usuarios/empresas
3. WHEN se actualizan precios de combustible THEN el sistema SHALL permitir definir precios para Diesel 500 y Diesel Premium específicos para la región NEA
4. WHEN se gestionan peajes THEN el sistema SHALL mostrar un mapa con ubicaciones de peajes y permitir editar tarifas individualmente
5. WHEN se modifican datos críticos THEN el sistema SHALL requerir confirmación y registrar un log de auditoría
6. WHEN se cargan datos masivos THEN el sistema SHALL permitir importación via CSV para peajes y precios
7. IF hay errores en la actualización de datos THEN el sistema SHALL mostrar mensajes específicos y mantener los datos anteriores

### Requirement 8: Generación de Reportes y Hoja de Ruta

**User Story:** Como jefe de logística, quiero generar reportes detallados y hojas de ruta simples, para que pueda documentar las decisiones, compartir información con choferes y facilitar la comunicación operativa.

#### Acceptance Criteria

1. WHEN se calcula una ruta THEN el sistema SHALL ofrecer opciones de "Generar Reporte Completo" y "Generar Hoja de Ruta Simple"
2. WHEN se genera un reporte completo THEN SHALL incluir: origen, destino, ruta recomendada, costos desglosados, ahorro estimado y comparación con alternativas
3. WHEN se genera una hoja de ruta simple THEN SHALL incluir: puntos clave del recorrido, distancia total, tiempo estimado y costo total
4. WHEN se crea cualquier reporte THEN el sistema SHALL permitir imprimirlo o descargarlo en PDF
5. WHEN se incluyen mapas en reportes THEN SHALL ser legibles, mostrar la ruta claramente y marcar puntos de peaje
6. WHEN se genera una hoja de ruta THEN el sistema SHALL crear una versión optimizada para visualización móvil
7. IF el reporte no se puede generar THEN el sistema SHALL informar el error específico y ofrecer alternativas