## from tensorFlow example, just use testing result part
## https://github.com/aymericdamien/TensorFlow-Examples/blob/master/examples/2_BasicModels/linear_regression.py
import os, sys, json, random, time
sys.path.append(os.path.dirname(sys.path[0]))
import numpy as np
#import tensorslow as ts
import tensorslow_he as ts
from utils.s3_helper import S3
import boto3
#import botocore

s3 = S3('selcrypt')

def linear_regression():
  tshe = ts.helper()
  
  xs = np.array(np.linspace(-2, 2, num=1000))
  xs_arr = tshe.list2array(xs)
 
  ts.Graph().as_default()
  rng = np.random

  # Parameters
  # tf Graph Input
  X = ts.placeholder()
  Y = ts.placeholder()

  # Set model weights
#  W = ts.Variable(he.encryptor_encoder.encode(rng.randn()))
#  b = ts.Variable(he.encryptor_encoder.encode(rng.randn()))
  W = ts.Variable(rng.randn())
  b = ts.Variable(rng.randn())
  # Construct a linear model
  pred = ts.add(ts.multiply(X, W), b)

  # Mean squared error
  const2 = ts.Variable(2)
  result = pred
  for i in (1, const2):
#    result = np.multiply(result, pred)
    result = ts.multiply(result, pred)
  cost = ts.reduce_sum(result)

  sess = ts.Session()
  # Run the initializer  
#  d =  ts.Variable(2 * xs_arr.shape[0])
  testing_cost = sess.run(ts.multiply(cost, ts.Variable(float(1/(2*xs_arr.shape[0])))), feed_dict={X: xs_arr})  # same function as cost above
  
  W_ = sess.run(W)
  b_ = sess.run(b)
  predict_Y = np.add(np.multiply(xs_arr, W_), b_)

  #print(he.decryptor_decoder.decode([testing_cost, predict_Y]))
  return [testing_cost, predict_Y]
  
def lambda_handler(event, context):
  start = time.time()
  r = linear_regression()
  for i, o in enumerate(r):
    print(type(o))
    if isinstance(o, np.ndarray):
      for j in range(len(o)):
        s3.upload_obj(o[j], "regression.res.{}.{}.out".format(i,j), "selcrypt", "/tmp/regression.res.{}.{}.out".format(i,j))
    else:
      s3.upload_obj(o, "regression.res.{}.out".format(i), "selcrypt", "/tmp/regression.res.{}.out".format(i))
  print("linear regression done")
  diff = time.time() - start
  client = boto3.client('iot-data', region_name='ap-northeast-1')
  response = client.publish(
    topic='selcrypt/out', 
    qos=0, 
    payload=json.dumps({'statusCode': 200, 'time': diff * 1000}))
  return json.dumps({'statusCode': 200, 'time': diff*1000})
