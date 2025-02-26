#!/bin/bash
set -xe           
set -o pipefail  # 파이프라인의 실패도 감지

AWS_REGION="ap-northeast-2"
AWS_REGION="ap-northeast-2"
AWS_ACCOUNT="013596862746"
REPOSITORY=hello-mlflow
TAG="latest"

# 0. start finch vm
finch vm start || true
 
# 1. Retrieve an authentication token and authenticate your Docker client to your registry.
# Use the AWS CLI:
aws ecr get-login-password --region $AWS_REGION | finch login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. build $REPOSITORY for amd64
finch build . --tag $REPOSITORY:$TAG --platform=amd64

# 3. After the build completes, tag your image so you can push the image to this repository:
finch tag $REPOSITORY:$TAG $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY:$TAG

# 4. Run the following command to push this image to your newly created AWS repository:
finch push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY:$TAG
