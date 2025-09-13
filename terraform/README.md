# Infraestructura de Kiro con Terraform

## Descripción

Este directorio contiene la configuración de infraestructura como código (IaC) para desplegar la aplicación Kiro en AWS utilizando Terraform.

## Componentes de Infraestructura

### Servicios AWS Utilizados
- **ECS (Elastic Container Service)**: Para ejecutar contenedores Docker
- **RDS (Relational Database Service)**: Base de datos PostgreSQL con PostGIS
- **Application Load Balancer**: Balanceo de carga para la aplicación
- **ECR (Elastic Container Registry)**: Registro de imágenes Docker
- **CloudWatch**: Monitoreo y logs
- **IAM**: Gestión de identidades y accesos
- **VPC**: Red virtual privada

### Arquitectura

```
Internet → Application Load Balancer → ECS Service → 
           ECS Tasks (Frontend + Backend) → RDS Database
```

## Requisitos Previos

1. **Terraform** instalado (versión 1.0 o superior)
2. **AWS CLI** configurado con credenciales válidas
3. **Cuenta AWS** con permisos suficientes
4. **Docker** para construir imágenes

## Configuración Inicial

1. **Copiar archivo de variables de ejemplo**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Editar terraform.tfvars** con valores reales:
   ```bash
   # Reemplazar con valores reales
   aws_account_id = "tu_account_id"
   vpc_id         = "tu_vpc_id"
   subnet_ids     = ["subnet_id_1", "subnet_id_2"]
   db_password    = "tu_contraseña_segura"
   secret_key     = "tu_clave_secreta"
   ```

## Despliegue

### Inicializar Terraform
```bash
terraform init
```

### Planificar los cambios
```bash
terraform plan
```

### Aplicar la configuración
```bash
terraform apply
```

### Destruir la infraestructura (solo en entornos de prueba)
```bash
terraform destroy
```

## Componentes Detallados

### ECS Cluster
- **Nombre**: kiro-cluster
- **Tipo**: Fargate (sin servidores)
- **Insights**: Habilitado para monitoreo

### Task Definition
- **Contenedores**: Backend (puerto 8000) y Frontend (puerto 80)
- **CPU**: 512 unidades
- **Memoria**: 1024 MB
- **Roles**: Configurados para acceso a logs y otros servicios

### Load Balancer
- **Tipo**: Application Load Balancer
- **Protocolo**: HTTP
- **Puerto**: 80
- **Health Check**: Verifica disponibilidad en /

### Base de Datos RDS
- **Engine**: Aurora PostgreSQL 13.7
- **Instancias**: 2 para alta disponibilidad
- **Clase**: db.t3.medium
- **Backup**: Retención de 7 días

### Seguridad
- **Security Groups**: Configurados para acceso controlado
- **IAM Roles**: Roles específicos para tareas ECS
- **Logs**: CloudWatch para monitoreo

## Variables de Configuración

| Variable | Descripción | Tipo | Valor por defecto |
|---------|-------------|------|-------------------|
| aws_region | Región de AWS | string | us-east-1 |
| aws_account_id | ID de cuenta AWS | string | - |
| vpc_id | ID de VPC | string | - |
| subnet_ids | Lista de IDs de subnets | list(string) | - |
| ssh_access_cidr | CIDR para acceso SSH | string | 0.0.0.0/0 |
| db_username | Usuario de base de datos | string | kiro_user |
| db_password | Contraseña de base de datos | string | - |
| secret_key | Clave secreta de aplicación | string | - |

## Salidas

Después del despliegue, Terraform proporciona las siguientes salidas:

- **load_balancer_dns**: DNS del balanceador de carga
- **database_endpoint**: Endpoint de la base de datos
- **ecs_cluster_name**: Nombre del cluster ECS

## Monitoreo y Logs

- **CloudWatch Logs**: Logs de contenedores en `/ecs/kiro-task`
- **Container Insights**: Métricas de rendimiento de ECS
- **Health Checks**: Monitoreo de disponibilidad de servicios

## Escalabilidad

La infraestructura está diseñada para escalar automáticamente:

1. **ECS Service**: Configurado con 2 tareas deseadas
2. **RDS**: Clúster multi-AZ para alta disponibilidad
3. **Load Balancer**: Distribuye tráfico entre tareas

## Seguridad

- **Network Security**: Security groups restringen el acceso
- **Data Encryption**: En tránsito y en reposo
- **IAM Roles**: Principio de mínimo privilegio
- **Secrets Management**: Variables sensibles marcadas como sensitive

## Mantenimiento

### Actualización de Infraestructura
```bash
# Planificar cambios
terraform plan

# Aplicar cambios
terraform apply
```

### Monitoreo de Logs
```bash
# Ver logs de CloudWatch
aws logs tail /ecs/kiro-task --follow
```

### Escalado Manual
Modificar `desired_count` en el servicio ECS o usar Auto Scaling.

## Costos Estimados

Los costos principales incluyen:

1. **ECS Fargate**: Basado en uso de vCPU y memoria
2. **RDS Aurora**: Basado en instancias y almacenamiento
3. **Load Balancer**: Basado en LCU (Load Balancer Capacity Units)
4. **CloudWatch**: Basado en volumen de logs

## Troubleshooting

### Problemas Comunes

1. **Permisos insuficientes**: Verificar políticas de IAM
2. **Conectividad de red**: Verificar security groups y subnets
3. **Variables no definidas**: Asegurar que terraform.tfvars esté completo
4. **Conflictos de nombres**: Cambiar nombres de recursos si es necesario

### Comandos Útiles

```bash
# Ver estado actual
terraform show

# Ver gráfico de dependencias
terraform graph

# Importar recursos existentes
terraform import <resource_type>.<resource_name> <resource_id>

# Validar configuración
terraform validate
```

## Mejores Prácticas

1. **Version Control**: Mantener configuraciones en Git
2. **State Management**: Usar backend remoto para estado de Terraform
3. **Modularización**: Dividir configuraciones en módulos reutilizables
4. **Documentación**: Mantener esta documentación actualizada
5. **Pruebas**: Probar cambios en entornos de desarrollo primero