# install cert-manager
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.16.2 \
  --set crds.enabled=true

catalogd_version=v1.1.0
install_default_catalogs=true
timeout_seconds=150s

kubectl apply -f "https://github.com/operator-framework/catalogd/releases/download/${catalogd_version}/catalogd.yaml"
# Wait for the rollout, and then wait for the deployment to be Available
kubectl rollout status --namespace="olmv1-system" "deployment/catalogd-controller-manager" --timeout="${timeout_seconds}"
kubectl wait --for=condition=Available "deployment/catalogd-controller-manager" --namespace="olmv1-system" --timeout="${timeout_seconds}"

if [[ "${install_default_catalogs}" != "false" ]]; then
    kubectl apply -f "https://github.com/operator-framework/catalogd/releases/download/${catalogd_version}/default-catalogs.yaml"
    kubectl wait --for=condition=Serving "clustercatalog/operatorhubio" --timeout="${timeout_seconds}"
fi

kubectl apply -f https://github.com/operator-framework/operator-controller/releases/download/v1.1.0/operator-controller.yaml
kubectl wait --for=condition=Available "deployment/operator-controller-controller-manager" --namespace="olmv1-system" --timeout="${timeout_seconds}"

kubectl apply -f resources/yaml/nodepool.yaml