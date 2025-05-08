# spark-operator

spark-operator를 사용하는 경우, operator pattern에따라 자동으로 driver/executor를 생성하고, job을 실행시킨다.

[+] sparkapplication crd spec
https://github.com/kubeflow/spark-operator/blob/v2.1.0/docs/api-docs.md#sparkoperator.k8s.io/v1beta2.SparkPodSpec

예시는 다음과 같다.
```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi
  namespace: default
spec:
  type: Scala
  mode: cluster
  image: spark:3.5.3
  imagePullPolicy: IfNotPresent
  mainClass: org.apache.spark.examples.SparkPi
  mainApplicationFile: local:///opt/spark/examples/jars/spark-examples.jar
  arguments:
  - "5000"
  sparkVersion: 3.5.3
  driver:
    labels:
      version: 3.5.3
    cores: 1
    memory: 512m
    serviceAccount: spark-operator-spark
  executor:
    labels:
      version: 3.5.3
    instances: 1
    cores: 1
    memory: 512m
```

spark를 jupyter에서 client 모드로 실행하는 것과 같이 jar/hadoop 설정이 필요하고, spec.sparkConf/spec.hadoopConf에 지정할 수 있다.
```yaml
sparkConf:
    spark.jars.packages: "org.apache.hadoop:hadoop-aws:3.3.4,software.amazon.awssdk:s3:2.31.30,software.amazon.awssdk:sts:2.31.30,software.amazon.awssdk:auth:2.31.30,org.apache.hadoop:hadoop-common:3.3.4,org.postgresql:postgresql:42.3.3"
    spark.kubernetes.file.upload.path: "s3a://spark"
    spark.jars.ivy: "/tmp/.ivy2"
  hadoopConf:
    fs.s3a.endpoint: "http://minio:80"
    fs.s3a.access.key: "xxx"
    fs.s3a.secret.key: "xxx"
    fs.s3a.impl: "org.apache.hadoop.fs.s3a.S3AFileSystem"
    fs.s3a.path.style.access: "true"
    fs.s3a.connection.ssl.enabled: "false"
    fs.s3a.aws.credentials.provider: "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider`
```

이렇게 설정하고 sparkapplications를 제출하면 다음과 같이 operator pod 동작한다.

Spark Operator Pod
├── spark-submit 실행
├── spark.jars.packages 확인
└── Ivy 캐싱
    └── $HOME/.ivy2/cache 접근 (기본 $HOME이 /home/spark) --> 권한 부족 (readonly)
└── Driver Pod 생성
    └── Executor Pod 생성

spark 설정 기본적으로 $HOME/.ivy2 하위 폴더에 해당 dependencies들을 설치하고, /opt/spark/jars에 jar 파일을 옮긴다.

그런데, 공식 spark image는 $HOME(/home/spark)은 readonly filesystem이라서 오류가 발생하기 때문에, 권한을 바꾸던가 해야한다.

기본적으로 spark-operator를 설치하면 /tmp 경로에 readonly: false로 설치되기 때문에 다음과 같이 ivy 경로를 tmp로 설정하면 쉽게 해결할 수 있다.
```yaml
spark.jars.ivy: "/tmp/.ivy2" 
```

다만, "spark.jars.packages"을 지정하면 항상 maven에 접근해서 jar 파일을 설치하기 때문에 네트워크 비용 및 설치하는데 시간이 소요된다.

따라서, custom spark를 만들어서 이용하는게 좋을 수 있다.
```dockerfile
# 폴더 구조
# ├── dockerfile
# └── jars
#     └── postgresql-42.3.3.jar
#     └── hadoop-aws-3.3.4.jar
#     ...
FROM spark:3.5.5

USER root
COPY ./jars/*.jar /opt/spark/jar`
USER spark
```

다음 예시 sparkapplication 이다.
```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi-python
  namespace: default
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster #cluster
  image: spark:3.5.5
  imagePullPolicy: IfNotPresent
  mainApplicationFile: s3a://spark/python/main.py
  sparkVersion: 3.5.5
  sparkConf:
    spark.jars.packages: "org.apache.hadoop:hadoop-aws:3.3.4,software.amazon.awssdk:s3:2.31.30,software.amazon.awssdk:sts:2.31.30,software.amazon.awssdk:auth:2.31.30,org.apache.hadoop:hadoop-common:3.3.4,org.postgresql:postgresql:42.3.3"
    spark.kubernetes.file.upload.path: "s3a://spark"
    spark.jars.ivy: "/tmp/.ivy2"
  hadoopConf:
    fs.s3a.endpoint: "http://minio:80"
    fs.s3a.access.key: "xxx"
    fs.s3a.secret.key: "xxx"
    fs.s3a.impl: "org.apache.hadoop.fs.s3a.S3AFileSystem"
    fs.s3a.path.style.access: "true"
    fs.s3a.connection.ssl.enabled: "false"
    fs.s3a.aws.credentials.provider: "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
  driver:
    cores: 1
    memory: 2g
    serviceAccount: spark-operator-spark
  executor:
    instances: 1
    cores: 1
    memory: 2g
    labels:
      type: spark-worker
    tolerations:
    - key: type
      operator: "Equal"
      value: spark-worker
      effect: "NoSchedule"
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: type
              operator: In
              values:
              - spark-worker   
```