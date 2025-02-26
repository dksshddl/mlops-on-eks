1. olmv1 + opend data hub catalog 생성하면 아래와 같은 오류를 확인할 수 있음
```log
E0205 04:19:26.649127       1 controller.go:316] "Reconciler error" err="source catalog content: error unpacking image: catalog image is missing the required label \"operators.operatorframework.io.index.configs.v1\"" controller="clustercatalog" controllerGroup="olm.operatorframework.io" controllerKind="ClusterCatalog" ClusterCatalog="opendatahub-operator" namespace="" name="opendatahub-operator" reconcileID="0203aa01-2f69-42e3-a3d3-b45c8e584e56"
```

해당 오류를 operator controller에서 확인해보면, 이미지내 특정 label "operators.operatorframework.io.index.configs.v1"이 존재하지않아 unpack이 불가능한 것을 알 수 있다.
https://github.com/operator-framework/operator-controller/blob/38b479584511c87c67ac7f39c1eb8ccc80967380/catalogd/internal/source/containers_image.go#L297

반면 olm v0에서는 해당 label을 검증하는 로직이 없다.

2. olmv0 + open data hub
    Message:               constraints not satisfiable: no operators found in package opendatahub-operator in the catalog referenced by subscription my-opendatahub-operator, subscription my-opendatahub-operator exists

# 2-1. catalog source 설치
# 2-2. Opendata hub가 존재하는지 확인
kubectl get packagemanifest -n olm | grep opendata
# 2-3. opendatahub subscriptions 생성 후 확인
kubectl get pod -n operators
NAME                                    READY   STATUS              RESTARTS   AGE
opendatahub-operator-5d668bbff4-vjz65   0/1     ContainerCreating   0          23s

## opendatahub operator controller error log in v1.5.0
➜ k logs opendatahub-operator-controller-manager-78647c4cd8-5g6mw -n operators
2025-02-05T13:01:51.191Z	ERROR	controller-runtime.source	if kind is a CRD, it should be installed before calling Start	{"kind": "ImageStream.image.openshift.io", "error": "no matches for kind \"ImageStream\" in version \"image.openshift.io/v1\""}
2025-02-05T13:01:51.191Z	ERROR	controller.kfdef-controller	Could not wait for Cache to sync	{"reconciler group": "kfdef.apps.kubeflow.org", "reconciler kind": "KfDef", "error": "failed to wait for kfdef-controller caches to sync: no matches for kind \"DeploymentConfig\" in version \"apps.openshift.io/v1\""}
sigs.k8s.io/controller-runtime/pkg/internal/controller.(*Controller).Start
	/opt/app-root/src/go/pkg/mod/sigs.k8s.io/controller-runtime@v0.10.0/pkg/internal/controller/controller.go:234
sigs.k8s.io/controller-runtime/pkg/manager.(*controllerManager).startRunnable.func1
	/opt/app-root/src/go/pkg/mod/sigs.k8s.io/controller-runtime@v0.10.0/pkg/manager/internal.go:696
2025-02-05T13:01:51.192Z	INFO	controller.secret-generator-controller	Shutdown signal received, waiting for all workers to finish	{"reconciler group": "", "reconciler kind": "Secret"}
2025-02-05T13:01:51.192Z	INFO	controller.secret-generator-controller	All workers finished	{"reconciler group": "", "reconciler kind": "Secret"}
2025-02-05T13:01:51.192Z	ERROR	setup	problem running manager	{"error": "failed to wait for kfdef-controller caches to sync: no matches for kind \"DeploymentConfig\" in version \"apps.openshift.io/v1\""}
runtime.goexit
	/usr/lib/golang/src/runtime/asm_amd64.s:1571

    Message:               constraints not satisfiable: subscription opendatahub-operator requires community-operators-redhat/olm/stable/opendatahub-operator.v1.1.1, subscription opendatahub-operator exists, clusterserviceversion opendatahub-operator.v1.5.0 exists and is not referenced by a subscription, @existing/operators//opendatahub-operator.v1.5.0 and community-operators-redhat/olm/stable/opendatahub-operator.v1.1.1 originate from package opendatahub-operator

    Message:               constraints not satisfiable: @existing/operators//opendatahub-operator.v1.5.0 and community-operators-redhat/olm/stable/opendatahub-operator.v1.1.1 provide KfDef (kfdef.apps.kubeflow.org/v1), subscription opendatahub-operator requires community-operators-redhat/olm/stable/opendatahub-operator.v1.1.1, subscription opendatahub-operator exists, clusterserviceversion opendatahub-operator.v1.5.0 exists and is not referenced by a subscription


# installation steps

kubectl apply -f resources/yaml/olmv0-odh-catalog-source.yaml

kubectl apply -f resources/yaml/olmv0-odh-subscription.yaml

# check install plan and approve plan manually
kubectl  get installplan -A
NAMESPACE   NAME            CSV                           APPROVAL   APPROVED
operators   install-fgrvs   opendatahub-operator.v1.1.1   Manual     false

kubectl patch installplans -n operators install-fgrvs -p '{"spec":{"approved":true}}' --type merge

Q. how to approve to instsall opendatahub??

installplan.operators.coreos.com/install-fgrvs patched

3. instsall keycloak and configurations keycloak

# review resources/yaml/keycloak.yaml
1. add "proxy-headers" and "KC_HOSTNAME" env
```yaml
--proxy-headers=xforwarded
...
- name: KC_HOSTNAME
  value: "keycloak.cjhyun.people.aws.dev"
```
# Configuration might need adjustments due to differences between nginx and AWS loadbalancer controllers
example 
- setting domain (add host settings to ingress)
- issue ca (see acm.tf)
- associate certificate to lb (associate certificate-arn to ingress)

4. odh
kubectl create ns ml-workshop
```sh
#!/bin/bash

domain="cjhyun.people.aws.dev"
input_file="resources/manifests/kfdef/ml-platform.yaml"
output_file="resources/manifests/kfdef/ml-platform-output.yaml"

services=("keycloak" "jupyterhub" "airflow" "minio" "mlflow")

cd ..

sed "" "s/${services[0]}\.<IP Address>\.nip\.io/${services[0]}.${domain}/g" $input_file > $output_file

for service in "${services[@]:1}"; do
    sed -i "" "s/${service}\.<IP Address>\.nip\.io/${service}.${domain}/g" $output_file
done
```


4-1. ingress configurations
```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: mlops-ingress-class
spec:
  controller: eks.amazonaws.com/alb
  parameters:
    apiGroup: eks.amazonaws.com
    kind: IngressClassParams
    # Use the name of the IngressClassParams set in the previous step
    name: mlops-ingress-class-params
---
apiVersion: eks.amazonaws.com/v1
kind: IngressClassParams
metadata:
  name: mlops-ingress-class-params
spec:
  group:
    name: mlops
```

4.2 jupyterhub install error
        exec(compiler(f.read(), fname, 'exec'), glob, loc)
      File "/opt/app-root/etc/jupyterhub_config.py", line 85, in <module>
        raise RuntimeError('Cannot calculate external host name for JupyterHub.')
    RuntimeError: Cannot calculate external host name for JupyterHub.