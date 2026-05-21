variable "aws_region" { default = "eu-north-1" }

variable "app_image" {
  description = "ECR image for FastAPI+Cron"
}

variable "meili_image" {
  description = "ECR image for MeiliSearch"
  default     = "getmeili/meilisearch:v1.7"
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "ecs_cluster_name" {
  default = "company-data-api-cluster"
}

variable "ecs_service_name" {
  default = "company-data-api-service"
}

variable "cpu"    { default = "1024" }
variable "memory" { default = "4096" }
