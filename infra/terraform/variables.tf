variable "aws_region" {
  type        = string
  default     = "eu-north-1"
  description = "AWS region"
}

variable "ecs_cluster_name" {
  type        = string
  default     = "company-data-api-cluster"
  description = "ECS cluster name"
}

variable "ecs_service_name" {
  type        = string
  default     = "company-data-api-service"
  description = "ECS service name"
}

variable "app_image" {
  type        = string
  default     = "509399624827.dkr.ecr.eu-north-1.amazonaws.com/company-api-repo:latest"
  description = "ECR image for FastAPI+Cron"
}

variable "meili_image" {
  type        = string
  default     = "getmeili/meilisearch:v1.7"
  description = "Docker image for MeiliSearch"
}

variable "app_port" {
  type        = number
  default     = 80
  description = "Application container port"
}

variable "cpu" {
  type        = string
  default     = "1024"
  description = "Fargate task CPU units"
}

variable "memory" {
  type        = string
  default     = "4096"
  description = "Fargate task memory (MiB)"
}

variable "hosted_zone_id" {
  type        = string
  description = "Route53 hosted zone ID"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS"
}
