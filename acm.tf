# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate_validation
locals {
  domain_lists = ["*"]
}

resource "aws_acm_certificate" "acm" {
  count = length(local.domain_lists)
  domain_name       = "${local.domain_lists[count.index]}.${var.domain_name}"
  validation_method = "DNS"
}

data "aws_route53_zone" "zone" {
  name         = var.domain_name
  private_zone = false
}

resource "aws_route53_record" "recored" {
  for_each = {
    for dvo in aws_acm_certificate.acm.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.zone.zone_id
}

resource "aws_acm_certificate_validation" "example" {
  certificate_arn         = aws_acm_certificate.acm.arn
  validation_record_fqdns = [for record in aws_route53_record.record : record.fqdn]
}