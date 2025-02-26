HOST=model.cjhyun.people.aws.dev

curl -vvvv -X POST "https://${HOST}/api/v1.0/predictions" \
  -H "Content-Type: application/json" \
  -d '{"data": {"ndarray": [[2,1]]}}' 


{
  "data": {
    "names": [
      "t:0",
      "t:1",
      "t:2",
      "t:3"
    ],
    "ndarray": [
      [
        0.25,
        0.25,
        0.25,
        0.25
      ]
    ]
  },
  "meta": {
    "requestPath": {
      "model-test-predictor": "013596862746.dkr.ecr.ap-northeast-2.amazonaws.com/hello-mlflow:latest"
    }
  }
}
