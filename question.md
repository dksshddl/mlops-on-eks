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