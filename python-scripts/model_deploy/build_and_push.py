import base64
import string
import subprocess
import os

import boto3
from botocore.config import Config

from minio import Minio
import mlflow
from mlflow.tracking import MlflowClient

HOST = "http://mlflow-tracking.default.svc.cluster.local:80"
EXPREIMENT_NAME = "HelloMlFlow"

os.environ['MLFLOW_S3_ENDPOINT_URL'] = "mlflow-minio.default.svc.cluster.local"
os.environ['AWS_REGION'] = 'ap-northeast-2'
os.environ['AWS_BUCKET_NAME'] = 'dksshddl-data'
os.environ['MLFLOW_TRACKING_USERNAME'] = 'user'
os.environ['MLFLOW_TRACKING_PASSWORD'] = 'dRgxazTbSF'
os.environ["MODEL_NAME"] = "cjhyun-model"
os.environ["MODEL_VERSION"] = "Version 1"

model_name = os.environ["MODEL_NAME"]
model_version = os.environ["MODEL_VERSION"]
build_name = f"seldon-model-{model_name}-v{model_version}"

def login_to_ecr():
    try:
        os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-2"
        # ECR 클라이언트 생성
        ecr_client = boto3.client('ecr')
        
        # 인증 토큰 가져오기
        response = ecr_client.get_authorization_token()
        
        # 인증 토큰 디코딩
        auth_token = response['authorizationData'][0]['authorizationToken']
        # decoded_auth_token = base64.b64decode(auth_token).decode('utf-8')
        # username, password = decoded_auth_token.split(':')
        
        # 레지스트리 엔드포인트 
        registry_url = response['authorizationData'][0]['proxyEndpoint']

        os.environ["CONTAINER_REGISTRY"] = registry_url
        os.environ["CONTAINER_REGISTRY_CREDS"] = auth_token

        kaniko_auth = string.Template('{"auths":{"$CONTAINER_REGISTRY":{"auth":"$CONTAINER_REGISTRY_CREDS"}}}').substitute(os.environ)

        # Docker 로그인
        print(kaniko_auth)
        with open("/kaniko/.docker/config.json", "w") as f:
            f.write(kaniko_auth)
        print("Successfully logged in to ECR")
        return True
        
    except Exception as e:
        print(f"Error logging in to ECR: {str(e)}")
        return False

def get_s3_server():
    minioClient = Minio(os.environ['MLFLOW_S3_ENDPOINT_URL'],
                        secure=False)

    return minioClient


def init():
    mlflow.set_tracking_uri(HOST)


def download_artifacts():
    print("retrieving model metadata from mlflow...")
    # model = mlflow.pyfunc.load_model(
    #     model_uri=f"models:/{model_name}/{model_version}"
    # )
    client = MlflowClient()

    model = client.get_registered_model(model_name)

    print(model)

    run_id = model._latest_version[0].run_id
    source = model._latest_version[0].source
    experiment_id = "1" # to be calculated from the source which is source='s3://mlflow/1/bf721e5641394ed6866baf20131fca20/artifacts/model'

    print("initializing connection to s3 server...")
    minioClient = get_s3_server()

    #     artifact_location = mlflow.get_experiment_by_name('rossdemo').artifact_location
    #     print("downloading artifacts from s3 bucket " + artifact_location)

    data_file_model = minioClient.fget_object("mlflow", f"/{experiment_id}/{run_id}/artifacts/model/model.pkl", "model.pkl")
    data_file_requirements = minioClient.fget_object("mlflow", f"/{experiment_id}/{run_id}/artifacts/model/requirements.txt", "requirements.txt")

    #Using boto3 Download the files from mlflow, the file path is in the model meta
    #write the files to the file system
    print("download successful")

    return run_id

    
def build_push_image():
    container_image = os.environ.get("CONTAINER_IMAGE", "my-ml-model")
    container_tag = os.environ.get("CONTAINER_TAG", "latest")

    
    container_location = string.Template(f"$CONTAINER_REGISTRY/{container_image}:{container_tag}").substitute(os.environ)
    print(container_location)
    #For docker repo, do not include the registry domain name in container location
    if os.environ["CONTAINER_REGISTRY"].find("docker.io") != -1:
        container_location= os.environ["CONTAINER_DETAILS"]
        
    full_command = "/kaniko/executor --context=" + os.getcwd() + " --dockerfile=Dockerfile --verbosity=debug --cache=true --single-snapshot=true --destination=" + container_location
    print(full_command)
    try:
        process = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(process.stdout)
        print(process.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit status {e.returncode}")
        print(f"stdout: {e.stdout.decode()}")
        print(f"stderr: {e.stderr.decode()}")
    
    
login_to_ecr()
get_s3_server()
init()
download_artifacts()
build_push_image()