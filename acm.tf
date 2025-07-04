# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate_validation

resource "aws_acm_certificate" "all_domain_acm" {
  domain_name       = "*.${var.domain_name}"
  validation_method = "DNS"
}

resource "aws_route53_record" "record" {
  for_each = {
    for dvo in aws_acm_certificate.all_domain_acm.domain_validation_options : dvo.domain_name => {
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
  certificate_arn         = aws_acm_certificate.all_domain_acm.arn
  validation_record_fqdns = [for record in aws_route53_record.record : record.fqdn]
}