## from tensorFlow example, just use testing result part
## https://github.com/danielsabinasz/TensorSlow/blob/master/examples/multi_layer_perceptron.py

import os, sys, json, random, time
sys.path.append(os.path.dirname(sys.path[0]))
import numpy as np
import tensorslow_he as ts
from utils.s3_helper import S3
import boto3
import botocore

s3 = S3('selcrypt')

def mlp() : 
  tshe = ts.helper()
    
  xs = np.array(np.linspace(-2, 2, num=30))
  ys = np.array(np.linspace(-2, 2, num=30))
  
  encrypted_xs = tshe.list2array(xs)
  encrypted_ys = tshe.list2array(ys)

  # Create a new graph
  ts.Graph().as_default()

  # Create training input placeholder
  X = ts.placeholder()

  #load model 
  # Build a hidden layer
  
  hweight = np.array(np.random.randn(2, 2))
  hbias = np.array(np.random.randn(2))

  W_hidden = ts.Variable(tshe.list2array(hweight))
  b_hidden = ts.Variable(tshe.list2array(hbias))
  p_hidden = ts.relu(ts.add(ts.matmul(X, W_hidden), b_hidden))

  print("output layer")
  # Build the output layer
  oweight =  np.array(np.random.randn(2, 2))
  obias = np.array(np.random.randn(2))
  
  W_output = ts.Variable(tshe.list2array(oweight))
  b_output = ts.Variable(tshe.list2array(obias))
  p_output = ts.relu(ts.add(ts.matmul(p_hidden, W_output), b_output))

  # Build cross-entropy loss
  # Create session

  session = ts.Session()

  pred_classes = []
  for x in xs:
    for y in ys:
      pred_class = session.run(p_output, feed_dict={X: [[x, y]]})[0]
      pred_classes.append((x, y, pred_class))

  return pred_classes

def lambda_handler(event, context):
  start = time.time()
  r = mlp()
  for i, o in enumerate(r):
    print(type(o))
    if isinstance(o, np.ndarray):
      for j in range(len(o)):
        s3.upload_obj(o[j], "mlp.res.{}.{}.out".format(i,j), "selcrypt", "/tmp/mlp.res.{}.{}.out".format(i,j))
    else:
      s3.upload_obj(o, "mlp.res.{}.out".format(i), "selcrypt", "/tmp/mlp.res.{}.out".format(i))
  print("mlp done")
  diff = time.time() - start
  client = boto3.client('iot-data', region_name='ap-northeast-1')
  response = client.publish(
    topic='selcrypt/out', 
    qos=0, 
    payload=json.dumps({'statusCode': 200, 'time': diff * 1000}))
  return json.dumps({'statusCode': 200, 'time': diff*1000})
