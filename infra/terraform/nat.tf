# REMOVE aws_route block — module already creates it

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
