# ML on EKS

## installation

### keycloak
➜ sed -i 's/<MY_ACM_ARN>/arn::xxx:xxx/g' resources/yaml/keycloak.yaml output.yaml
➜ sed -i 's/<MY_HOSTNAME>/example.com/g' resources/yaml/keycloak.yaml

k apply -f resoureces/yaml/keycloak.yaml

elyra..
--
    An existing Apache Airflow cluster
        Ensure Apache Airflow is at least v1.10.8 and below v2.0.0. Other versions might work but have not been tested.
        Apache Airflow is configured to use the Kubernetes Executor.
        The airflow-notebook operator package is installed on the webserver, scheduler, and workers.
--

--> need to build v4.0 on my own


--> just replace jinja template, it works well in my lab.
--> but airflow worker failed with following error
```
Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--100  1364  100  1364    0     0  25069      0 --:--:-- --:--:-- --:--:-- 25259
Requirement already satisfied: packaging in /home/airflow/.local/lib/python3.12/site-packages (24.2)

[notice] A new release of pip is available: 25.0 -> 25.0.1
[notice] To update, run: pip install --upgrade pip
[I 04:53:04.104] 'hello_world':'hello' - starting operation
[I 04:53:04.104] 'hello_world':'hello' - Installing packages
[E 04:53:04.104] This version of Python '3.12' is not supported for Elyra generic components
Traceback (most recent call last):
  File "/opt/airflow/jupyter-work-dir/bootstrapper.py", line 554, in <module>
    main()
  File "/opt/airflow/jupyter-work-dir/bootstrapper.py", line 540, in main
    OpUtil.package_install()
  File "/opt/airflow/jupyter-work-dir/bootstrapper.py", line 385, in package_install
    elyra_packages = cls.package_list_to_dict(requirements_file)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/airflow/jupyter-work-dir/bootstrapper.py", line 440, in package_list_to_dict
    with open(filename) as fh:
         ^^^^^^^^^^^^^^
TypeError: expected str, bytes or os.PathLike object, not NoneType
```