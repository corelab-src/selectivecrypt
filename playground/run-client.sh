#!/bin/sh
if [ $# -ne 1 ]; then
  echo "Usage: $0 <path/to/client.py>"
  exit 1 
else
  python $1
fi
