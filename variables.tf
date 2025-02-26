variable "vpc_id" {
  type = string
}

variable "alb_arn" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "admin_roles" {
  type = list(string)
}

variable "cluster_name" {
  type = string
}