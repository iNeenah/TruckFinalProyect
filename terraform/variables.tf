# Variables de AWS
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

# Variables de seguridad
variable "ssh_access_cidr" {
  description = "CIDR block for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

# Variables de base de datos
variable "db_username" {
  description = "Database username"
  type        = string
  default     = "kiro_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Variables de aplicación
variable "secret_key" {
  description = "Secret key for the application"
  type        = string
  sensitive   = true
}