# ============================================================================
# CivicQ - AWS Infrastructure Variables
# ============================================================================

# ============================================================================
# General Configuration
# ============================================================================
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "civicq"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

# ============================================================================
# VPC Configuration
# ============================================================================
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

# ============================================================================
# Database Configuration (RDS PostgreSQL)
# ============================================================================
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"  # Smallest for development/testing
  # Production recommendation: db.t4g.medium or larger
}

variable "db_allocated_storage" {
  description = "Initial storage allocation in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage allocation in GB (autoscaling)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "civicq"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "civicq_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 16
    error_message = "Database password must be at least 16 characters."
  }
}

variable "db_backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

# ============================================================================
# Redis Configuration (ElastiCache)
# ============================================================================
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t4g.micro"
  # Production recommendation: cache.t4g.small or larger
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes (1 = no replication, 2+ = with replication)"
  type        = number
  default     = 1

  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 6
    error_message = "Number of cache nodes must be between 1 and 6."
  }
}

variable "redis_auth_token" {
  description = "Redis authentication token (password)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.redis_auth_token) >= 16
    error_message = "Redis auth token must be at least 16 characters."
  }
}

# ============================================================================
# S3 and CloudFront Configuration
# ============================================================================
variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"  # US, Canada, Europe
  # Options: PriceClass_100, PriceClass_200, PriceClass_All
}

variable "cors_allowed_origins" {
  description = "CORS allowed origins for S3 bucket"
  type        = list(string)
  default     = ["https://civicq.com", "https://www.civicq.com"]
}

# ============================================================================
# ECS Configuration
# ============================================================================
variable "ecs_backend_cpu" {
  description = "CPU units for backend task (256 = 0.25 vCPU)"
  type        = number
  default     = 512  # 0.5 vCPU
}

variable "ecs_backend_memory" {
  description = "Memory for backend task in MB"
  type        = number
  default     = 1024  # 1 GB
}

variable "ecs_backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

variable "ecs_worker_cpu" {
  description = "CPU units for Celery worker task"
  type        = number
  default     = 512
}

variable "ecs_worker_memory" {
  description = "Memory for Celery worker task in MB"
  type        = number
  default     = 1024
}

variable "ecs_worker_desired_count" {
  description = "Desired number of Celery worker tasks"
  type        = number
  default     = 2
}

# ============================================================================
# Application Configuration
# ============================================================================
variable "docker_image_backend" {
  description = "Docker image for backend (from ECR or Docker Hub)"
  type        = string
  default     = ""
}

variable "docker_image_frontend" {
  description = "Docker image for frontend (from ECR or Docker Hub)"
  type        = string
  default     = ""
}

variable "app_secret_key" {
  description = "Application secret key for JWT signing"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.app_secret_key) >= 32
    error_message = "Application secret key must be at least 32 characters."
  }
}

variable "frontend_url" {
  description = "Frontend application URL"
  type        = string
  default     = "https://civicq.com"
}

variable "backend_url" {
  description = "Backend API URL"
  type        = string
  default     = "https://api.civicq.com"
}

# ============================================================================
# Domain and SSL Configuration
# ============================================================================
variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "ARN of ACM certificate for HTTPS"
  type        = string
  default     = ""
}

# ============================================================================
# Monitoring and Logging
# ============================================================================
variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights for ECS"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 7
}

# ============================================================================
# Tags
# ============================================================================
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
