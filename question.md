1. Jupyer notebook 실행시, hub pod가 jupyter notebook pod를 실행함(jupyter-admin)
pvc, pv를 어떻게 관리해야하지? springclean이 pv를 자꾸 죽임 -> auto-delete:no


2. 현재 s3에 artifact가 저장되지 않음
minio
minio123

3. seldon 배포후, alb ingress에 붙였는데 404에러가 나옴 (해결 완료)
service 직접 호출시 잘 됨

curl -vvvv -X POST "https://model.cjhyun.people.aws.dev/api/v1.0/predictions" \
          -H "Content-Type: application/json"
          -d '{"data": {"ndarray": [[2,1]]}}'
---
k exec nginx-aws -- curl -X POST model-test:8000/api/v1.0/predictions \
                          -H "Content-Type: application/json" \
                          -d '{"data": {"ndarray": [[2,1]]}}'

4. airflow
- Default Webserver (Airflow UI) Login credentials:
    username: admin
    password: admin
- Default Postgres connection credentials:
    username: postgres
    password: postgres
    port: 5432

  airflow 설치시 전부 request/limit이 없어서 omm 발생하는 것으로 보입, 적절한 값은 어떻게 찾지?
  hpa가 적용되어있으면 만능인가? scheduler는 한개가 처리할 거 같은데 hpa가 의미가 있을까 

- git 설정 시, sub path를 넣어줄 수 는 없나?
git-sync까지는 잘 되는데..

- elyra pipeline 이용시, airflow dag 생성과 관련된 dependency 오류가 있음..
```
"ModuleNotFoundError: No module named 'a`rflow.contrib.kubernetes'"
```
https://github.com/elyra-ai/elyra/blob/cbd7aa8c59872592afad922af8758de63eab06dc/elyra/pipeline/airflow/airflow_processor.py#L83-L93
https://github.com/elyra-ai/elyra/pull/2819

https://elyra.readthedocs.io/en/v2.1.0/recipes/configure-airflow-as-a-runtime.html
dag에 python 파일이 추가되는데, dependency는 어디를 물고있는지 디버깅하려면 뭘봐야하는지??

5. managed service와 비용 비교

6. jupyter pod는  "automountServiceAccountToken: false" 로 kubeapi-access가 안들어감.


➜ k get pod -n airflow model-deploy-jftwximu -oyaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: "2025-04-23T06:20:10Z"
  labels:
    airflow_kpo_in_cluster: "True"
    airflow_version: 2.9.3
    dag_id: modeL_deploy-0416083718
    kubernetes_pod_operator: "True"
    run_id: manual__2025-04-23T061957.1290120000-b70705113
    task_id: model_deploy
    try_number: "1"
  name: model-deploy-jftwximu
  namespace: airflow
  resourceVersion: "52794261"
  uid: 32e164c4-8529-4bf1-8d0f-560d23789d8c
spec:
  affinity: {}
  containers:
  - args:
    - 'mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo ''Downloading
      https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py''
      && curl --fail -H ''Cache-Control: no-cache'' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py
      --output bootstrapper.py && echo ''Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt''
      && curl --fail -H ''Cache-Control: no-cache'' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt
      --output requirements-elyra.txt && python3 -m pip install packaging && python3
      -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name
      ''modeL_deploy'' --cos-endpoint http://minio.default.svc.cluster.local --cos-bucket
      airflow --cos-directory ''s3:/dksshddl-bucket/model-build-and-deploy/modeL_deploy-0416083718''
      --cos-dependencies-archive ''model_deploy-ee01d863-840e-4da4-8cad-074ba3f40311.tar.gz''
      --file ''mode_deploy_pipeline/model_deploy/model_deploy.py'' '
    command:
    - sh
    - -c
    env:
    - name: EXPERIMENT_ID
      value: "1"
    - name: MODEL_NAME
      value: my-model
    - name: MODEL_COORDINATES
      value: 013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/my-ml-model:latest
    - name: INGRESS_HOST
      value: model.cjhyun.people.aws.dev
    - name: ELYRA_RUNTIME_ENV
      value: airflow
    - name: AWS_ACCESS_KEY_ID
      value: minio
    - name: AWS_SECRET_ACCESS_KEY
      value: minio123
    - name: ELYRA_ENABLE_PIPELINE_INFO
      value: "True"
    - name: ELYRA_RUN_NAME
      value: modeL_deploy-20250423T061957
    - name: AWS_STS_REGIONAL_ENDPOINTS
      value: regional
    - name: AWS_DEFAULT_REGION
      value: ap-northeast-2
    - name: AWS_REGION
      value: ap-northeast-2
    - name: AWS_ROLE_ARN
      value: arn:aws:iam::013596862746:role/eks-pod-role
    - name: AWS_WEB_IDENTITY_TOKEN_FILE
      value: /var/run/secrets/eks.amazonaws.com/serviceaccount/token
    image: 013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/ml-on-eks/python-custom:latest
    imagePullPolicy: Always
    name: base
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-chqnh
      readOnly: true
    - mountPath: /var/run/secrets/eks.amazonaws.com/serviceaccount
      name: aws-iam-token
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  nodeName: i-0bf3bc60b2e038405
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Never
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: default
  serviceAccountName: default
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: aws-iam-token
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          audience: sts.amazonaws.com
          expirationSeconds: 86400
          path: token
  - name: kube-api-access-chqnh
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
status:
  conditions:
  - lastProbeTime: null
    lastTransitionTime: "2025-04-23T06:20:38Z"
    status: "True"
    type: PodReadyToStartContainers
  - lastProbeTime: null
    lastTransitionTime: "2025-04-23T06:20:10Z"
    status: "True"
    type: Initialized
  - lastProbeTime: null
    lastTransitionTime: "2025-04-23T06:20:38Z"
    status: "True"
    type: Ready
  - lastProbeTime: null
    lastTransitionTime: "2025-04-23T06:20:38Z"
    status: "True"
    type: ContainersReady
  - lastProbeTime: null
    lastTransitionTime: "2025-04-23T06:20:10Z"
    status: "True"
    type: PodScheduled
  containerStatuses:
  - containerID: containerd://d412c4798dbf05b4dff42867b7d5378ea558e60c308899d604b2302a4bdaae79
    image: 013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/ml-on-eks/python-custom:latest
    imageID: 013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/ml-on-eks/python-custom@sha256:db80c551f1256f104e06f8b07345f143ed14429095eba1c89b9158809a671608
    lastState: {}
    name: base
    ready: true
    restartCount: 0
    started: true
    state:
      running:
        startedAt: "2025-04-23T06:20:37Z"
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-chqnh
      readOnly: true
      recursiveReadOnly: Disabled
    - mountPath: /var/run/secrets/eks.amazonaws.com/serviceaccount
      name: aws-iam-token
      readOnly: true
      recursiveReadOnly: Disabled
  hostIP: 10.0.174.211
  hostIPs:
  - ip: 10.0.174.211
  phase: Running
  podIP: 10.0.175.70
  podIPs:
  - ip: 10.0.175.70
  qosClass: BestEffort
  startTime: "2025-04-23T06:20:10Z"