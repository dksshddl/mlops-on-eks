# ML on EKS

## installation

### keycloak
➜ sed -i 's/<MY_ACM_ARN>/arn::xxx:xxx/g' resources/yaml/keycloak.yaml output.yaml
➜ sed -i 's/<MY_HOSTNAME>/example.com/g' resources/yaml/keycloak.yaml

k apply -f resoureces/yaml/keycloak.yaml