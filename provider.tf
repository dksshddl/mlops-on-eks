terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.84.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.25.2"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = "ap-northeast-2"  # Change this to your desired region
  
  # Optional: If you need to specify a profile
  # profile = "default"
  
  # Optional: If you need to assume a role
  # assume_role {
  #   role_arn     = "arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME"
  #   session_name = "terraform-session"
  # }

  default_tags {
    tags = {
      Environment = "mlops"           # Optional: Add default tags
      Terraform   = "true"
      # Add more default tags as needed
    }
  }
}

provider "kubernetes" {
  host                   = aws_eks_cluster.mlops.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.mlops.certificate_authority[0].data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.mlops.name]
  }
}