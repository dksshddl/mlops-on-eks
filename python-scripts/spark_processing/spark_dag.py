from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "spark-0502045040",
}

dag = DAG(
    dag_id="spark-0502045040",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `spark.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: spark_pipeline/python/create_crd.py

op_1bb43b4b_b4b7_4b4c_9e7c_b08f2efe9e95 = KubernetesPodOperator(
    name="create_crd",
    namespace="airflow",
    image="013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/ml-on-eks/python-custom:latest",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'spark' --cos-endpoint http://minio.default.svc.cluster.local --cos-bucket airflow --cos-directory 'spark-0502045040' --cos-dependencies-archive 'create_crd-1bb43b4b-b4b7-4b4c-9e7c-b08f2efe9e95.tar.gz' --file 'spark_pipeline/python/create_crd.py' "
    ],
    task_id="create_crd",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "spark-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file=None,
    dag=dag,
)

op_1bb43b4b_b4b7_4b4c_9e7c_b08f2efe9e95.image_pull_policy = "Always"
