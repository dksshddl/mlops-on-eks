#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

olmv1_manifest=https://github.com/operator-framework/operator-controller/releases/download/v1.2.0-rc4/operator-controller.yaml

if [[ -z "$olmv1_manifest" ]]; then
    echo "Error: Missing required MANIFEST variable"
    exit 1
fi

default_catalogs_manifest="https://github.com/operator-framework/operator-controller/releases/download/v1.2.0-rc4/default-catalogs.yaml"
cert_mgr_version=v1.15.3
install_default_catalogs=true

if [[ -z "$cert_mgr_version" ]]; then
    echo "Error: Missing CERT_MGR_VERSION variable"
    exit 1
fi

kubectl_wait() {
    namespace=$1
    runtime=$2
    timeout=$3

    kubectl wait --for=condition=Available --namespace="${namespace}" "${runtime}" --timeout="${timeout}"
}

kubectl_wait_rollout() {
    namespace=$1
    runtime=$2
    timeout=$3

    kubectl rollout status --namespace="${namespace}" "${runtime}" --timeout="${timeout}"
}

kubectl_wait_for_query() {
    manifest=$1
    query=$2
    timeout=$3
    poll_interval_in_seconds=$4

    if [[ -z "$manifest" || -z "$query" || -z "$timeout" || -z "$poll_interval_in_seconds" ]]; then
        echo "Error: Missing arguments."
        echo "Usage: kubectl_wait_for_query <manifest> <query> <timeout> <poll_interval_in_seconds>"
        exit 1
    fi

    start_time=$(date +%s)
    while true; do
        val=$(kubectl get "${manifest}" -o jsonpath="${query}" 2>/dev/null || echo "")
        if [[ -n "${val}" ]]; then
            echo "${manifest} has ${query}."
            break
        fi
        if [[ $(( $(date +%s) - start_time )) -ge ${timeout} ]]; then
            echo "Timed out waiting for ${manifest} to have ${query}."
            exit 1
        fi
        sleep ${poll_interval_in_seconds}s
    done
}

kubectl apply -f "https://github.com/cert-manager/cert-manager/releases/download/${cert_mgr_version}/cert-manager.yaml"
# Wait for cert-manager to be fully ready
kubectl_wait "cert-manager" "deployment/cert-manager-webhook" "60s"
kubectl_wait "cert-manager" "deployment/cert-manager-cainjector" "60s"
kubectl_wait "cert-manager" "deployment/cert-manager" "60s"
kubectl_wait_for_query "mutatingwebhookconfigurations/cert-manager-webhook" '{.webhooks[0].clientConfig.caBundle}' 60 5
kubectl_wait_for_query "validatingwebhookconfigurations/cert-manager-webhook" '{.webhooks[0].clientConfig.caBundle}' 60 5

kubectl apply -f "${olmv1_manifest}"
# Wait for the rollout, and then wait for the deployment to be Available
kubectl_wait_rollout "olmv1-system" "deployment/catalogd-controller-manager" "60s"
kubectl_wait "olmv1-system" "deployment/catalogd-controller-manager" "60s"
kubectl_wait "olmv1-system" "deployment/operator-controller-controller-manager" "60s"

if [[ "${install_default_catalogs}" != "false" ]]; then
    kubectl apply -f "${default_catalogs_manifest}"
    kubectl wait --for=condition=Serving "clustercatalog/operatorhubio" --timeout="60s"
fi
