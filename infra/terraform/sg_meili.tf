resource "aws_security_group" "meili" {
  name        = "meili-sg"
  description = "Allow app to reach Meili"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Allow app service to reach Meili"
    from_port       = 7700
    to_port         = 7700
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
