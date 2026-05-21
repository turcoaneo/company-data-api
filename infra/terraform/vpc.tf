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
