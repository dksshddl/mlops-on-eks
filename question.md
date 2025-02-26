1. Jupyer notebook 실행시, hub pod가 jupyter notebook pod를 실행함(jupyter-admin)
pvc, pv를 어떻게 관리해야하지? springclean이 pv를 자꾸 죽임


2. 현재 s3에 artifact가 저장되지 않음

3. seldon 배포후, alb ingress에 붙였는데 404에러가 나옴
service 직접 호출시 잘 됨

curl -vvvv -X POST "https://model.cjhyun.people.aws.dev/api/v1.0/predictions" \
          -H "Content-Type: application/json" \
          -d '{"data": {"ndarray": [[2,1]]}}'

---
k exec nginx-aws -- curl -X POST model-test:8000/api/v1.0/predictions \
                          -H "Content-Type: application/json" \
                          -d '{"data": {"ndarray": [[2,1]]}}'

4. airflow
Default Webserver (Airflow UI) Login credentials:
    username: admin
    password: admin
Default Postgres connection credentials:
    username: postgres
    password: postgres
    port: 5432

  airflow 설치시 전부 request/limit이 없어서 omm 발생하는 것으로 보입, 적절한 값은 어떻게 찾지?
  hpa가 적용되어있으면 만능인가? scheduler는 한개가 처리할 거 같은데 hpa가 의미가 있을까 