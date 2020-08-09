#!/bin/sh
aws lambda invoke \
  --endpoint http://localhost:9001 \
  --invocation-type RequestResponse \
  --no-sign-request \
  --function-name myfun \
  --payload '{"body":"Test"}' \
  data/output.json
