provider "aws" {
  region = var.aws_region
}

# -------------------------
# VPC
# -------------------------
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "company-data-api-vpc"
  cidr   = "10.1.0.0/16"

  azs             = ["eu-north-1a", "eu-north-1b"]
  public_subnets  = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnets = ["10.1.3.0/24", "10.1.4.0/24"]

  enable_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true
}

# -------------------------
# ECS Cluster
# -------------------------
resource "aws_ecs_cluster" "this" {
  name = var.ecs_cluster_name
}

# -------------------------
# IAM Roles
# -------------------------
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_iam_role" "task_role" {
  name = "company-data-api-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

# -------------------------
# CloudWatch Logs
# -------------------------
resource "aws_cloudwatch_log_group" "logs" {
  name              = "/ecs/company-data-api"
  retention_in_days = 7
}

# -------------------------
# Security Groups
# -------------------------
resource "aws_security_group" "alb" {
  name        = "company-api-alb-sg"
  description = "Allow HTTP/HTTPS"
  vpc_id      = module.vpc.vpc_id

  ingress { from_port = 80  to_port = 80  protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 443 to_port = 443 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "ecs" {
  name        = "company-api-ecs-sg"
  description = "Allow ALB to reach ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}

# -------------------------
# Load Balancer
# -------------------------
resource "aws_lb" "this" {
  name               = "company-api-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}

resource "aws_lb_target_group" "this" {
  name        = "tg-company-api"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

# -------------------------
# ECS Task Definition (2 containers)
# -------------------------
resource "aws_ecs_task_definition" "this" {
  family                   = "company-data-api-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory

  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    # -------------------------
    # Container 1: FastAPI + Cron
    # -------------------------
    {
      name      = "app"
      image     = var.app_image
      essential = true

      portMappings = [{
        containerPort = var.app_port
        protocol      = "tcp"
      }]

      environment = [
        { name = "MEILI_URL", value = "http://meili:7700" },
        { name = "APP_ENV",   value = "uat" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "app"
        }
      }
    },

    # -------------------------
    # Container 2: MeiliSearch
    # -------------------------
    {
      name      = "meili"
      image     = var.meili_image
      essential = true

      portMappings = [{
        containerPort = 7700
        protocol      = "tcp"
      }]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "meili"
        }
      }
    }
  ])
}

# -------------------------
# ECS Service
# -------------------------
resource "aws_ecs_service" "this" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = "app"
    container_port   = var.app_port
  }
}
