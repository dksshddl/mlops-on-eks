data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:type"
    values = ["public"]  # Replace with your tag value
  }
}

data "aws_subnets" "private_primary" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:type"
    values = ["private"]  # Replace with your tag value
  }

  filter {
    name   = "tag-key"
    values = ["primary"]  # Replace with your tag value
  }
}

data "aws_subnets" "private_secondary" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:type"
    values = ["private"]  # Replace with your tag value
  }

  filter {
    name   = "tag-key"
    values = ["secondary"]  # Replace with your tag value
  }
}

data "aws_subnets" "isolated" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:type"
    values = ["isolated"]  # Replace with your tag value
  }
}

data "aws_route53_zone" "zone" {
  name         = var.domain_name
  private_zone = false
}

data "aws_lb" "lb" {
  arn  = var.alb_arn
}