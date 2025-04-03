import base64
import string
import os

import boto3
from botocore.config import Config

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

def build_push_image():
    container_location = string.Template("$CONTAINER_REGISTRY/$CONTAINER_DETAILS").substitute(os.environ)
    
    #For docker repo, do not include the registry domain name in container location
    if os.environ["CONTAINER_REGISTRY"].find("docker.io") != -1:
        container_location= os.environ["CONTAINER_DETAILS"]
        
    full_command = "/kaniko/executor --context=" + os.getcwd() + " --dockerfile=Dockerfile --verbosity=debug --cache=true --single-snapshot=true --destination=" + container_location
    print(full_command)
    process = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(process.stdout)
    print(process.stderr)
    
login_to_ecr()
build_push_image()