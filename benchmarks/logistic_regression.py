## from tensorFlow example, just use testing result part
## https://github.com/aymericdamien/TensorFlow-Examples/blob/master/examples/2_BasicModels/logistic_regression.py
import os, sys, json, random, time
sys.path.append(os.path.dirname(sys.path[0]))
import numpy as np
#import tensorslow as ts
import tensorslow_he as ts
from utils.s3_helper import S3
import boto3

s3 = S3('selcrypt')

def logistic_regression() :
  #tshe = ts.TensorslowHelper(he)
  tshe = ts.helper()
  
  xs = np.array(np.linspace(0, 256, num=300))
  ys = np.array([1])
  
  encrypted_xs = tshe.list2array(xs)
  encrypted_ys = tshe.list2array(ys)

  ts.Graph().as_default()

  # Parameters
  # tf Graph Input
  x = ts.placeholder()
  y = ts.placeholder()

  # Set model weights
  W = ts.Variable(tshe.list2array(np.zeros([300, 4])))
  b = ts.Variable(tshe.list2array(np.zeros([4])))

  # Construct a linear model
  pred = ts.sigmoid(ts.add(ts.matmul(x, W), b))
  cost = ts.reduce_mean(ts.negative(ts.multiply(y, ts.log(pred))))
  sess = ts.Session()
  # Run the initializer  
  d =  ts.Variable(2 * encrypted_xs.shape[0])
  testing_cost = sess.run(ts.div(cost, d), feed_dict={x: encrypted_xs, y: encrypted_ys})  # same function as cost above
  
  result = sess.run(pred, feed_dict={x : encrypted_xs})

  return [testing_cost, result]

def lambda_handler(event, context):
  start = time.time()
  r = logistic_regression()
  for i, o in enumerate(r):
    if isinstance(o, np.ndarray):
      for j in range(len(o)):
        #print(o[j])
        o[j].save('tmp/logistic_regression.res.{}.{}.out'.format(i,j))
        s3.upload_obj(o[j], "/tmp/logistic_regression.res.{}.{}.out".format(i,j), 'selcrypt', 'logistic_regression.res.{}.{}.out'.format(i,j))
    else:
      #print(o)
      o.save('tmp/logistic_regression.res.{}.out'.format(i))
      s3.upload_obj(o, "/tmp/logistic_regression.res.{}.out".format(i), 'selcrypt', 'logistic_regression.res.{}.out'.format(i))
  print("logistic regression done")
  diff = time.time() - start
  client = boto3.client('iot-data', region_name='ap-northeast-1')
  response = client.publish(
    topic='selcrypt/out', 
    qos=0, 
    payload=json.dumps({'statusCode': 200, 'time': diff * 1000}))
  return json.dumps({'statusCode': 200, 'time': diff*1000})
