resource "aws_ecs_service" "meili" {
  name            = "meili-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.meili.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.meili.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.meili.arn
  }
}

resource "aws_service_discovery_service" "meili" {
  name = "meili"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.this.id

    dns_records {
      ttl  = 5
      type = "A"
    }
  }

}
