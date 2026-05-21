resource "aws_ecs_task_definition" "meili" {
  family                   = "meili-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = "meili"
      image     = "getmeili/meilisearch:v1.7"
      essential = true

      portMappings = [
        {
          containerPort = 7700
          hostPort      = 7700
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "MEILI_NO_ANALYTICS", value = "true" }
      ]
    }
  ])
}
