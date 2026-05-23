terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.2.8"
    }
  }

  backend "s3" {
    bucket         = "company-data-api-tf-state"
    key            = "terraform.tf-state"
    region         = "eu-north-1"
    use_lockfile   = true
    encrypt        = true
  }
}
