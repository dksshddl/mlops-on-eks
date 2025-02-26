#!/bin/bash

domain="cjhyun.people.aws.dev"
input_file="resources/manifests/kfdef/ml-platform.yaml"
output_file="resources/manifests/kfdef/ml-platform-output.yaml"

services=("keycloak" "jupyterhub" "airflow" "minio" "mlflow" "grafana")

cd ..
sed "s/${services[0]}\.<IP Address>\.nip\.io/${services[0]}.${domain}/g" $input_file > $output_file

for service in "${services[@]:1}"; do
    sed -i "" "s/${service}\.<IP Address>\.nip\.io/${service}.${domain}/g" $output_file
done