# Proveedor de AWS
provider "aws" {
  region = var.aws_region
}

# Grupo de seguridad para la aplicación
resource "aws_security_group" "kiro_sg" {
  name        = "kiro-security-group"
  description = "Security group for Kiro application"
  vpc_id      = var.vpc_id

  # Reglas de entrada
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_access_cidr]
    description = "SSH access"
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.kiro_db_sg.id]
    description = "PostgreSQL access from application"
  }

  # Reglas de salida
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "kiro-security-group"
  }
}

# Grupo de seguridad para la base de datos
resource "aws_security_group" "kiro_db_sg" {
  name        = "kiro-db-security-group"
  description = "Security group for Kiro database"
  vpc_id      = var.vpc_id

  # Reglas de entrada
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.kiro_sg.id]
    description     = "PostgreSQL access from application"
  }

  # Reglas de salida
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "kiro-db-security-group"
  }
}

# Cluster ECS
resource "aws_ecs_cluster" "kiro_cluster" {
  name = "kiro-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "kiro-cluster"
  }
}

# Registro de tareas ECS
resource "aws_ecs_task_definition" "kiro_task" {
  family                   = "kiro-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "kiro-backend"
      image     = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/kiro-backend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_rds_cluster.kiro_db.endpoint}:5432/kiro"
        },
        {
          name  = "SECRET_KEY"
          value = var.secret_key
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/kiro-task"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    },
    {
      name      = "kiro-frontend"
      image     = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/kiro-frontend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/kiro-task"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "kiro-task-definition"
  }
}

# Servicio ECS
resource "aws_ecs_service" "kiro_service" {
  name            = "kiro-service"
  cluster         = aws_ecs_cluster.kiro_cluster.id
  task_definition = aws_ecs_task_definition.kiro_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.kiro_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.kiro_tg.arn
    container_name   = "kiro-frontend"
    container_port   = 80
  }

  depends_on = [
    aws_lb_listener.kiro_listener
  ]

  tags = {
    Name = "kiro-service"
  }
}

# Balanceador de carga
resource "aws_lb" "kiro_lb" {
  name               = "kiro-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.kiro_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "kiro-load-balancer"
  }
}

# Grupo de destino del balanceador
resource "aws_lb_target_group" "kiro_tg" {
  name     = "kiro-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "kiro-target-group"
  }
}

# Listener del balanceador
resource "aws_lb_listener" "kiro_listener" {
  load_balancer_arn = aws_lb.kiro_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kiro_tg.arn
  }

  tags = {
    Name = "kiro-listener"
  }
}

# Base de datos RDS (Aurora PostgreSQL)
resource "aws_rds_cluster" "kiro_db" {
  cluster_identifier      = "kiro-db-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = "13.7"
  availability_zones      = ["us-east-1a", "us-east-1b", "us-east-1c"]
  database_name           = "kiro"
  master_username         = var.db_username
  master_password         = var.db_password
  backup_retention_period = 7
  preferred_backup_window = "02:00-03:00"
  vpc_security_group_ids  = [aws_security_group.kiro_db_sg.id]

  tags = {
    Name = "kiro-db-cluster"
  }
}

resource "aws_rds_cluster_instance" "kiro_db_instance" {
  count              = 2
  identifier         = "kiro-db-instance-${count.index}"
  cluster_identifier = aws_rds_cluster.kiro_db.id
  instance_class     = "db.t3.medium"
  engine             = "aurora-postgresql"
  publicly_accessible = false

  tags = {
    Name = "kiro-db-instance-${count.index}"
  }
}

# Registro de logs CloudWatch
resource "aws_cloudwatch_log_group" "/ecs/kiro-task" {
  name = "/ecs/kiro-task"
  retention_in_days = 30

  tags = {
    Name = "kiro-log-group"
  }
}

# Rol de ejecución de tareas ECS
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "kiro-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Política para el rol de ejecución de tareas ECS
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Rol de tareas ECS
resource "aws_iam_role" "ecs_task_role" {
  name = "kiro-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Política para el rol de tareas ECS
resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "kiro-ecs-task-role-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Salidas
output "load_balancer_dns" {
  value = aws_lb.kiro_lb.dns_name
  description = "DNS name of the load balancer"
}

output "database_endpoint" {
  value = aws_rds_cluster.kiro_db.endpoint
  description = "Endpoint of the database cluster"
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.kiro_cluster.name
  description = "Name of the ECS cluster"
}