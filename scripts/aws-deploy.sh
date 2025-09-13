#!/bin/bash

# Script de despliegue en AWS

# Variables de configuración
AWS_REGION="us-east-1"
ECR_REPOSITORY="kiro-app"
CLUSTER_NAME="kiro-cluster"
SERVICE_NAME="kiro-service"
TASK_DEFINITION="kiro-task"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI no está instalado"
    exit 1
fi

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

# Iniciar sesión en ECR
print_message "Iniciando sesión en ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -ne 0 ]; then
    print_error "Error al iniciar sesión en ECR"
    exit 1
fi

# Construir y subir imagen del backend
print_message "Construyendo imagen del backend..."
cd backend
docker build -t $ECR_REPOSITORY-backend -f Dockerfile.prod .

if [ $? -ne 0 ]; then
    print_error "Error al construir imagen del backend"
    exit 1
fi

print_message "Subiendo imagen del backend a ECR..."
docker tag $ECR_REPOSITORY-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-backend:latest

if [ $? -ne 0 ]; then
    print_error "Error al subir imagen del backend a ECR"
    exit 1
fi

# Construir y subir imagen del frontend
print_message "Construyendo imagen del frontend..."
cd ../frontend
docker build -t $ECR_REPOSITORY-frontend -f Dockerfile.prod .

if [ $? -ne 0 ]; then
    print_error "Error al construir imagen del frontend"
    exit 1
fi

print_message "Subiendo imagen del frontend a ECR..."
docker tag $ECR_REPOSITORY-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-frontend:latest

if [ $? -ne 0 ]; then
    print_error "Error al subir imagen del frontend a ECR"
    exit 1
fi

# Actualizar definición de tarea ECS
print_message "Actualizando definición de tarea ECS..."
cd ..
aws ecs register-task-definition \
    --family $TASK_DEFINITION \
    --task-role-arn arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole \
    --execution-role-arn arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole \
    --network-mode awsvpc \
    --requires-compatibilities EC2 FARGATE \
    --cpu "512" \
    --memory "1024" \
    --container-definitions "[
        {
            \"name\": \"kiro-backend\",
            \"image\": \"$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-backend:latest\",
            \"portMappings\": [
                {
                    \"containerPort\": 8000,
                    \"hostPort\": 8000,
                    \"protocol\": \"tcp\"
                }
            ],
            \"environment\": [
                {
                    \"name\": \"DATABASE_URL\",
                    \"value\": \"postgresql://user:password@kiro-db.cluster.amazonaws.com:5432/kiro\"
                }
            ],
            \"logConfiguration\": {
                \"logDriver\": \"awslogs\",
                \"options\": {
                    \"awslogs-group\": \"/ecs/$TASK_DEFINITION\",
                    \"awslogs-region\": \"$AWS_REGION\",
                    \"awslogs-stream-prefix\": \"ecs\"
                }
            }
        },
        {
            \"name\": \"kiro-frontend\",
            \"image\": \"$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY-frontend:latest\",
            \"portMappings\": [
                {
                    \"containerPort\": 80,
                    \"hostPort\": 80,
                    \"protocol\": \"tcp\"
                }
            ],
            \"logConfiguration\": {
                \"logDriver\": \"awslogs\",
                \"options\": {
                    \"awslogs-group\": \"/ecs/$TASK_DEFINITION\",
                    \"awslogs-region\": \"$AWS_REGION\",
                    \"awslogs-stream-prefix\": \"ecs\"
                }
            }
        }
    ]"

if [ $? -ne 0 ]; then
    print_error "Error al actualizar definición de tarea ECS"
    exit 1
fi

# Actualizar servicio ECS
print_message "Actualizando servicio ECS..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $TASK_DEFINITION \
    --force-new-deployment

if [ $? -ne 0 ]; then
    print_error "Error al actualizar servicio ECS"
    exit 1
fi

# Esperar a que el servicio se actualice
print_message "Esperando a que el servicio se actualice..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME

if [ $? -ne 0 ]; then
    print_error "Error al esperar a que el servicio se actualice"
    exit 1
fi

print_message "Despliegue completado exitosamente!"
print_message "La aplicación debería estar disponible en unos minutos."