## custom spark

spark는 client/cluster 모드로나뉨

client -> spark-submit하는 주체가 driver가 됨
cluster -> spark cluster endppint에 driver/executor를 생성요청을함

* driver - spark 코드를 지정하고, executor에 작업을 분배
* executor - 실제로 데이터를 처리하는 작업자. 데이터를 partition으로 나눠 여러 executor가 병렬로 처리

## case study 
Jupyerhub에서 client로 사용시..

Jupyerhub pod에서 pyspark 코드를 실행시키기 때문에 driver 역할을 합니다.

따라서 Jupyerhub에 spark가 설치되어있어야합니다.

* 공식 이미지 목록은 다음 문서에서 확인 가능합니다. [1]

jupyter/pyspark-notebook 이미지는 기본적으로 지정하지않은 경우, spark latest의 이미지를 사용합니다.

현재 spark의 latest는 4.0.0으로, preview 상태입니다. [2]

따라서 원하는 spark 버전으로 jupyter 허브를 빌드해주어야 하고 예제 코드는 다음과 같습니다. 
[+] 공식 github 참고 - https://github.com/jupyter/docker-stacks/tree/main/images/pyspark-notebook
```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG REGISTRY=quay.io
ARG OWNER=jupyter
ARG BASE_IMAGE=$REGISTRY/$OWNER/scipy-notebook
FROM $BASE_IMAGE

LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

# Fix: https://github.com/hadolint/hadolint/wiki/DL4006
# Fix: https://github.com/koalaman/shellcheck/wiki/SC3014
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Spark dependencies
# Default values can be overridden at build time
# (ARGS are in lowercase to distinguish them from ENV)
ARG openjdk_version="17"

RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    "openjdk-${openjdk_version}-jre-headless" \
    ca-certificates-java && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# If spark_version is not set, latest Spark will be installed
ARG spark_version="3.5.5"
ARG hadoop_version="3"
# If scala_version is not set, Spark without Scala will be installed
ARG scala_version
# URL to use for Spark downloads
# You need to use https://archive.apache.org/dist/spark/ website if you want to download old Spark versions
# But it seems to be slower, that's why we use the recommended site for download
ARG spark_download_url="https://dlcdn.apache.org/spark/"

ENV SPARK_HOME=/usr/local/spark
ENV PATH="${PATH}:${SPARK_HOME}/bin"
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info"

COPY setup_spark.py /opt/setup-scripts/
RUN chmod 755 /opt/setup-scripts/setup_spark.py
# Setup Spark
RUN /opt/setup-scripts/setup_spark.py \
    --spark-version="${spark_version}" \
    --hadoop-version="${hadoop_version}" \
    --scala-version="${scala_version}" \
    --spark-download-url="${spark_download_url}"

# Configure IPython system-wide
COPY ipython_kernel_config.py "/etc/ipython/"
RUN fix-permissions "/etc/ipython/"

USER ${NB_UID}

# Install pyarrow
# NOTE: It's important to ensure compatibility between Pandas versions.
# The pandas version in this Dockerfile should match the version
# on which the Pandas API for Spark is built.
# To find the right version:
# 1. Check out the Spark branch you are on: <https://github.com/apache/spark>
# 2. Find the pandas version in the file `dev/infra/Dockerfile`.
RUN mamba install --yes \
    'grpcio-status' \
    'grpcio' \
    'pandas=2.2.2' \
    'pyarrow' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

WORKDIR "${HOME}"
EXPOSE 4040
```

또한 해당 spark image에는 s3/postgresql에 연결하기 위한 package가 필요합니다.
간단하게 다음과 같이 sparkConf로 설정이 가능하며, maven 형식으로 작성하면 maven에서 가져옵니다.
```python
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,software.amazon.awssdk:bundle:2.31.30,org.apache.hadoop:hadoop-common:3.3.4,org.postgresql:postgresql:42.3.3")
```

spark 3.5.5 + hadoop-3.3.4 를 사용하는 이유는 호환성이 보증되는 가장 안정적이어서 입니다.. 제 환경에서 spark 4.0 + hadoop 3.4.1 으로 여러차례 테스트해보았는데, class not found 등 잦은 오류가 발생하였습니다..


다음은 이를 기반으로 driver에서 spark executor를 생성하는 에제 코드입니다.
```
import os
import socket

from pyspark.sql import SparkSession

current_pod_ip = socket.gethostbyname(socket.gethostname())

spark = SparkSession.builder.master("k8s://https://kubernetes.default.svc.cluster.local")\
        .appName("spark")\
        .config("spark.executor.instances", 1) \
        .config("spark.submit.deployMode", "client") \
        .config("spark.driver.host", current_pod_ip) \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.driver.port", "29413") \
        .config("spark.ui.port", "4040") \
        .config("spark.kubernetes.namespace", "default") \
        .config("spark.kubernetes.container.image", "apache/spark:3.5.5") \
        .config("spark.kubernetes.container.image.pullPolicy", "Always") \
        .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
        .config("spark.kubernetes.authenticate.executor.serviceAccountName", "spark") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,software.amazon.awssdk:bundle:2.31.30,org.apache.hadoop:hadoop-common:3.3.4,org.postgresql:postgresql:42.3.3") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:80") \
        .config("spark.hadoop.fs.s3a.access.key", "minio") \
        .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()
```


이 때, spark.driver.host에 "current_pod_ip"를 추가한 이유는 기본적으로 localhost를 요청하기 때문에, 지정하지 않으면 Executor가 생성되지 않았습니다.


[1] Selecting an Image
https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html

[2] quay - spark image
https://quay.io/repository/jupyter/all-spark-notebook?tab=tags