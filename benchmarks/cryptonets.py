import time, json, os, sys
from utils.s3_helper import S3
import boto3
import tempfile
import zipfile

from concurrent import futures
from io import BytesIO

s3 = S3('selcrypt')

def add_many(dots):
  dotsum = dots[0]
  for i in range(1, len(dots)):
    dotsum = dotsum + dots[i]
  return dotsum


def cryptonets():
  x1 = 15
  
  p_conv_len = 5*25
  c_conv_len = x1*25
  p_conv_vec = []
  c_conv_vec = []
   
  for i in range(0, p_conv_len):
    p = s3.download_obj('selcrypt', 'p_conv_vec.{}.in'.format(i), '/tmp/p_conv_vec.{}.in'.format(i))
    p_conv_vec.append(p)
  for i in range(0, c_conv_len):
    c = s3.download_obj('selcrypt', 'c_conv_vec.{}.in'.format(i), '/tmp/c_conv_vec.{}.in'.format(i))
    c_conv_vec.append(c)

  p_pool_len = 100*5*x1
  p_pool_vec = []

  for i in range(0, p_pool_len):
    po = s3.download_obj('selcrypt', 'p_pool_vec.{}.in'.format(i), '/tmp/p_pool_vec.{}.in'.format(i))
    p_pool_vec.append(po)
  
  p_fc_len = 10*100
  p_fc_vec = []
  for i in range(0, p_fc_len) :
    f = s3.download_obj('selcrypt', 'p_fc_vec.{}.in'.format(i), '/tmp/p_fc_vec.{}.in'.format(i))
    p_fc_vec.append(f)

  video = s3.download_obj('selcrypt', 'video_small.mp4', '/tmp/video_small.mp4')

  print("...Downloading inputs and weights is done\n")
  print("Calculating Conv 1 ...\n")

  dot_len = 25
  conv_out = []

  for i in range(0, p_conv_len, dot_len) :
    for j in range(0, c_conv_len, dot_len) :
      dots = []
      for x in range(0,dot_len) :
        #print(i,j,x)
        c_tpm = c_conv_vec[j+x] * p_conv_vec[i+x]
        dots.append(c_tpm)
      conv_out.append(add_many(dots))

  del p_conv_vec[:]
  del c_conv_vec[:]

  print("...Conv 1 is done\n")
  print("Calculating activation layer 1 (square)...\n")

  act_out = []
  for i in range(0, len(conv_out)) :
    c_tpm = conv_out[i] * conv_out[i]
    act_out.append(c_tpm)

  del conv_out[:]

  print("...Activation layer 1 is done\n")
  print("Calculating pool + linear...\n")

  dot_len = 5*x1
  c_pool_len = 5*x1
  pool_out = []

  for i in range(0, p_pool_len, dot_len) :
    for j in range(0, c_pool_len, dot_len) :
      dots = []
      for x in range(0, dot_len) :
        c_tpm = act_out[j+x] * p_pool_vec[i+x]
        dots.append(c_tpm)
      pool_out.append(add_many(dots))

  del act_out[:]
  del p_pool_vec[:]


  print("...Pool+Linear layer  is done\n")
  print("Calculating activation layer 2 (square)...\n")

  act_out_2 = []
  for i in range(0, len(pool_out)) :
    c_tpm = pool_out[i] * pool_out[i]
    act_out_2.append(c_tpm)

  del pool_out[:]

  print("...Activation layer 2 is done\n")
  print("Calculating FC layer...\n")

  dot_len = 100
  c_fc_len = 100
  fc_out = []

  for i in range(0, p_fc_len, dot_len) :
    for j in range(0, c_fc_len, dot_len) :
      dots = []
      for x in range(0, dot_len) :
        c_tpm = act_out_2[j+x] * p_fc_vec[i+x]
        dots.append(c_tpm)
      fc_out.append(add_many(dots))

  print("...FC layer is done\n")
  s3.upload_obj(video, '/tmp/video_small.mp4', 'selcrypt', 'video_small.mp4')
  return fc_out

def lambda_handler(event, context):
  start = time.time()
  s3.extract_and_upload('selcrypt', 'all_inputs.zip')
  r = cryptonets()
  res_list = []
  for i, o in enumerate(r):
    o.save('/tmp/res.{}.out'.format(i))
    res_list.append('/tmp/res.{}.out'.format(i))
    #s3.upload_obj(o, '/tmp/res.{}.out'.format(i), 'selcrypt',
    #  'res.{}.out'.format(i))
  s3.compress_and_upload('selcrypt', res_list, 'all_outputs.zip')
  print('cryptonets done')
  diff = time.time() - start
  client = boto3.client('iot-data', region_name='ap-northeast-1')
  response = client.publish(
    topic='selcrypt/out', 
    qos=0, 
    payload=json.dumps({'statusCode': 200, 'time': diff * 1000}))
  return json.dumps({'statusCode': 200, 'time': diff * 1000})
