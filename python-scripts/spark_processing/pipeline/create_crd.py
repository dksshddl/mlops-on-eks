import os
import yaml

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from jinja2 import Template


# run_id = os.environ["EXPERIMENT_ID"]
# model_name = os.environ["MODEL_NAME"]
# model_container_location = os.environ["MODEL_COORDINATES"]
# ingress_host = os.environ["INGRESS_HOST"]

def init_kube_config():
    config.load_incluster_config()

def create_spark_from_file(namespace : str):
    # template_data = { "experiment_id": run_id, 
    #                  "model_name": model_name, 
    #                  "model_coordinates": model_container_location, 
    #                  "ingress_host": ingress_host, 
    #                  "namespace" : namespace }
    # rendered_template = seldon_template.render(template_data)
    # template_to_yaml = yaml.safe_load(rendered_template)
    
    spark_template = Template(open("spark-pi.yaml").read())
    spark_yaml = yaml.safe_load(spark_template.render())

    api_instance = client.CustomObjectsApi()

    group = "sparkoperator.k8s.io"
    version = "v1beta2"
    plural = "sparkapplications"
    name = f"spark-pi"

    api_instance.create_namespaced_custom_object(group=group, version=version, plural=plural, namespace=namespace, body=spark_yaml)                                                    

# 사용 예시
if __name__ == "__main__":
    namespace = "default"
    init_kube_config()
    create_spark_from_file(namespace)