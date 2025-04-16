import os

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from jinja2 import Template


run_id = os.environ["EXPERIMENT_ID"]
model_name = os.environ["MODEL_NAME"]
model_container_location = os.environ["MODEL_COORDINATES"]
ingress_host = os.environ["INGRESS_HOST"]

def init_kube_config():
    config.load_incluster_config()

def apply_sheldon_from_file(namespace : str):
    template_data = {"experiment_id": run_id, "model_name": model_name, "model_coordinates": model_container_location, "ingress_host": ingress_host}
    seldon_template = Template(open("SeldonDeploy.yaml").read())
    rendered_template = seldon_template.render(template_data)

    api_instance = client.CustomObjectsApi()

    group = "machinelearning.seldon.io"
    version = "v1"
    plural = "seldondeployments"
    name = f"{model_name}-predictor"

    try:
        api_instance.get_namespaced_custom_object(group=group, version=version, plural=plural, name=name, namespace=namespace)

        api_instance.patch_cluster_custom_object(group=group, version=version, plural=plural, name=name, body=rendered_template)
    except ApiException as e:
        if e.status == 404:
            api_instance.create_namespaced_custom_object(group=group, version=version, plural=plural, name=name, body=rendered_template)
        else:
            print(f"Error applying SeldonDeployment: {e}")
            raise

def apply_ingress(namespace : str):

    # API 클라이언트 생성
    api_instance = client.NetworkingV1Api()

    # Ingress 객체 정의
    client.V1Ingress
    ingress = client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(
            name="sheldon-ingress",
            namespace=namespace,
            annotations={
                "alb.ingress.kubernetes.io/scheme": "internet-facing",
                "alb.ingress.kubernetes.io/target-type": "ip",
                "alb.ingress.kubernetes.io/listen-ports": '[{"HTTP": 80}, {"HTTPS":443}]',
                "alb.ingress.kubernetes.io/ssl-redirect": '443',
                "alb.ingress.kubernetes.io/healthcheck-port": '8000',
                "alb.ingress.kubernetes.io/healthcheck-path": "/ready",
                "alb.ingress.kubernetes.io/success-codes": '200'
            },
        ),
        spec=client.V1IngressSpec(
        ingress_class_name="mlops-ingress-class",
        rules=[
            client.V1IngressRule(
                host="model.cjhyun.people.aws.dev",
                http=client.V1HTTPIngressRuleValue(
                    paths=[
                        client.V1HTTPIngressPath(
                            path="/",
                            path_type="Prefix",
                            backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    name=f"model-{run_id}-{model_name}",
                                    port=client.V1ServiceBackendPort(
                                        number=8000
                                    )
                                )
                            )
                        )
                    ]
                )
            )
        ]
        )
    )
  
    try:
        # 먼저 Ingress가 존재하는지 확인
        api_instance.read_namespaced_ingress(name="sheldon-ingress", namespace=namespace)
        # 존재한다면 업데이트
        api_instance.patch_namespaced_ingress(
            name="sheldon-ingress",
            namespace=namespace,
            body=ingress
        )
        print(f"Ingress updated in namespace {namespace}")
    except ApiException as e:
        if e.status == 404:
            # 존재하지 않으면 생성
            api_instance.create_namespaced_ingress(
                namespace=namespace,
                body=ingress
            )
            print(f"Ingress created in namespace {namespace}")
        else:
            print(f"Exception when applying ingress: {e}")

# 사용 예시
if __name__ == "__main__":
    namespace = "default"
    apply_sheldon_from_file(namespace)
    apply_ingress(namespace)

    