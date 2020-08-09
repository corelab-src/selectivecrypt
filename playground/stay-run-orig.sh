#!/bin/sh
docker run --user=root:root --rm \
  -v "$PWD":/var/task \
  -v "$PWD"/opt:/opt \
  -e DOCKER_LAMBDA_STAY_OPEN=1 \
  -p 9001:9001 \
  lambci/lambda:python3.7 \
  lambda.lambda_handler
