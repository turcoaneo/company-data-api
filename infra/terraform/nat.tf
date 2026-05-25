resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = module.vpc.public_subnets[0]

  tags = {
    Name = "company-nat-gateway"
  }
}

resource "aws_route" "private_nat_routes" {
  for_each = toset(module.vpc.private_route_table_ids)

  route_table_id         = each.value
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat.id
}
