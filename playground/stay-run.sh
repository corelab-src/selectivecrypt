#!/bin/sh
if [ $# -ne 2 ]; then
  echo "Usage: $0 <lambda_transformed> <lambda_handler>"
  exit 1
else
  docker run --user=root:root --rm \
    -v "$PWD":/var/task \
    -v "$PWD"/opt:/opt \
    -e DOCKER_LAMBDA_STAY_OPEN=1 \
    -p 9001:9001 \
    lambci/lambda:python3.7 \
    $1.$2
fi
