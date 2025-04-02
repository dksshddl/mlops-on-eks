
locals {
  services=["keycloak", "jupyterhub", "airflow", "minio", "mlflow", "grafana", "model", "airflow"]
}

resource "aws_route53_record" "www" {
  count = length(local.services)
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = "${local.services[count.index]}.${var.domain_name}"
  type    = "A"
  
  alias {
    name = data.aws_lb.lb.dns_name
    zone_id = data.aws_lb.lb.zone_id
    evaluate_target_health = true
  }
}