## from tensorFlow example, just use testing result part
## https://github.com/danielsabinasz/TensorSlow/blob/master/examples/perceptron.py

import os, sys, json, random, time
sys.path.append(os.path.dirname(sys.path[0]))
import numpy as np
#import tensorslow as ts
import tensorslow_he as ts
from utils.s3_helper import S3
import boto3
#import botocore

s3 = S3('selcrypt')

datanum = 40

def perceptron() :
  tshe = ts.helper()
    
  #generate data
  xs = np.array(np.linspace(-2, 2, num=datanum))
  ys = np.array(np.linspace(-2, 2, num=datanum))
  #encrypt data
  xs = tshe.list2array(xs)
  ys = tshe.list2array(ys)

  # Create a new graph
  ts.Graph().as_default()

  X = ts.placeholder()

  # Initialize weights randomly
  oweight = np.array(np.random.randn(2, 2))
  obias = np.array(np.random.randn(2))

  W = ts.Variable(tshe.list2array(oweight))
  b = ts.Variable(tshe.list2array(obias))
  
  # Build perceptron
  p = ts.relu(ts.add(ts.matmul(X, W), b))

  # Create session
  session = ts.Session()
  
  pred_classes = []
  for x in xs:
    for y in ys:
      pred_class = session.run(p, feed_dict={X: [[x, y]]})[0]
      pred_classes.append((x, y, pred_class))

  return pred_classes

def lambda_handler(event, context):
  start = time.time()
  r = perceptron()
  return_body=[]
  if isinstance(r, list):
    for i, o in enumerate(r):
      if isinstance(o, np.ndarray):
        for j in range(len(o)):
          print(o)
          s3.upload_obj(o[j], "perceptron.res.{}.{}.out".format(i,j), "selcrypt", "/tmp/perceptron.res.{}.{}.out".format(i,j))
          return_body.append("perceptron.res.{}.{}.out".format(i,j))
      elif isinstance(o, tuple):
        for j, oo in enumerate(o):
          s3.upload_obj(oo, "perceptron.res.{}.{}.out".format(i,j), "selcrypt", "/tmp/perceptron.res.{}.{}.out".format(i,j))
          return_body.append("perceptron.res.{}.{}.out".format(i,j))
      else:
        s3.upload_obj(o, "perceptron.res.{}.out".format(i), "selcrypt", "/tmp/perceptron.res.{}.out".format(i))
        return_body.append("perceptron.res.{}.out".format(i))
  else:
    s3.upload_obj(r, "perceptron.res.out", "selcrypt", "/tmp/perceptron.res.out")
    return_body.append("perceptron.res.out")
    
  print("perceptron done")
  diff = time.time() - start
  client = boto3.client('iot-data', region_name='ap-northeast-1')
  response = client.publish(
    topic='selcrypt/out', 
    qos=0, 
    payload=json.dumps({'statusCode': 200, 'time': diff * 1000}))
  return json.dumps({'statusCode': 200, 'time': diff*1000})
