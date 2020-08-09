import os, sys, json, random, time
sys.path.append(os.path.dirname(sys.path[0]))

from utils.mypyheal import MyPyHeal as ph
from pyheal import wrapper
#from pyheal import encoders
from utils.s3_helper import S3
import utils.network as net
import utils.cryptfile as cryptfile
import utils.awsiot as awsiot
import numpy as np
import tensorslow_he as ts

ENC_MODE="enc" # "enc" or "noenc"

# global vars.
s3 = S3()
tx_start = 0
total_start = 0

# This callback prints performance results from the lambda
def callback(client, userdata, message):
  arrival_time = time.time()
  tx_diff = arrival_time - tx_start
  total_diff = arrival_time - total_start
  print("[Client] Received a new message: ")
  print(message.payload)
  print("[Client] from topic: ")
  print(message.topic)
  print("[Client] Tx time {} ms".format(tx_diff))
  print("[Client] Total time {} ms".format(total_diff))
  print("--------------\n")

def linear_regression_prepare_inputs_and_transmit_no_offload(destdir, mode, cf, he):
  x1 = 10
  start = time.time()

  if mode[:2] == 'he':
    #cf.encrypt_file_with_he('data', 'playground/input_data/video_small.mp4')
    encrypted_file = cf.encrypt_file_with_he('data', 'playground/input_data/image_tiny.png', he)
  elif mode[:2] == 'se':
    cf.encrypt_file('data/', 'playground/input_data/image_tiny.png')
  else:
    print("[Client] Wrong mode")
    sys.exit()

  tshe = ts.helper(he)

  print("Generating pseudo-weights ...\n")
  xs = np.array(np.linspace(-2, 2, num=1000))
  xs_arr = tshe.list2array(xs)

  print("...pseudo-weights for Conv 1, Pool and FC complete\n")
  for i in range(0, p_conv_len):
    if ENC_MODE == "noenc":
      np.savetxt(os.path.join(destdir, "p_conv_vec." + str(i) + ".in"), [p_conv_vec[i]])
    else:
      p_conv_vec[i].save(os.path.join(destdir, "p_conv_vec." + str(i) + ".in"))
  for i in range(0, c_conv_len):
    if ENC_MODE == "noenc":
      np.savetxt(os.path.join(destdir, "c_conv_vec." + str(i) + ".in"), [c_conv_vec[i]])
    else:
      c_conv_vec[i].save(os.path.join(destdir, "c_conv_vec." + str(i) + ".in"))
  for i in range(0, p_pool_len):
    if ENC_MODE == "noenc":
      np.savetxt(os.path.join(destdir, "p_pool_vec." + str(i) + ".in"), [p_pool_vec[i]])
    else:
      p_pool_vec[i].save(os.path.join(destdir, "p_pool_vec." + str(i) + ".in"))
  for i in range(0, p_fc_len):
    if ENC_MODE == "noenc":
      np.savetxt(os.path.join(destdir, "p_fc_vec." + str(i) + ".in"), [p_fc_vec[i]])
    else:
      p_fc_vec[i].save(os.path.join(destdir, "p_fc_vec." + str(i) + ".in"))
  
  for i, vec in enumerate(encrypted_file):
    vec.save(os.path.join(destdir, "image_tiny.png.{}.enc".format(i)))
  
  diff = time.time() - start
  print("Encrypt and Save: done in {} ms".format(diff*1000))
  
  tx_start = time.time()

  os.system('cd data && zip -q -r all_inputs.zip . && cd -')
  s3.upload_file('data/all_inputs.zip', 'selcrypt', 'all_inputs.zip')
  
  """
  if mode[:1] == 'he':
    s3.upload_file(os.path.join(destdir, "video_small.mp4.he.enc"), "selcrypt", "video_small.mp4.he.enc") 
  elif mode[:1] == 'se':
    s3.upload_file(os.path.join(destdir, "video_small.mp4.enc"), "selcrypt", "video_small.mp4.enc")
  else:
    print("[Client] Wrong mode")
    sys.exit()
  
  for i in range(0, p_conv_len):
    s3.upload_file(os.path.join(destdir, "p_conv_vec.{}.in".format(i)), "selcrypt", "p_conv_vec.{}.in".format(i))
  for i in range(0, c_conv_len):
    s3.upload_file(os.path.join(destdir, "c_conv_vec.{}.in".format(i)), "selcrypt", "c_conv_vec.{}.in".format(i))
  for i in range(0, p_pool_len):
    s3.upload_file(os.path.join(destdir, "p_pool_vec.{}.in".format(i)), "selcrypt", "p_pool_vec.{}.in".format(i))
  for i in range(0, p_fc_len):
    s3.upload_file(os.path.join(destdir, "p_fc_vec.{}.in".format(i)), "selcrypt", "p_fc_vec.{}.in".format(i))
  """

def linear_regression_no_offload(mode, client_for_awsiot):
  client_for_awsiot.connect_and_subscribe(callback)
  start = time.time()
  # he init
  poly_modulus = 1 << 12
  coeff_modulus = 1 << 13
  plain_modulus = 1099511922689
  #plain_modulus = 786433
  he = ph(poly_modulus, coeff_modulus, plain_modulus)
  he.saveParmsAndKeys("data/"); # data/seal.parms, data/pub.key
  diff = time.time() - start
  print("[Client] HE Init: done in {} ms".format(diff*1000))

  #s3.upload_file("data/seal.parms", "selcrypt", "seal.parms")
  #s3.upload_file("data/pub.key", "selcrypt", "pub.key")
  #s3.upload_file("data/relin.key", "selcrypt", "relin.key")
  #diff = time.time() - start
  #print("[Client] HE parms and keys Uploading: done in {} ms".format(diff*1000))
  
  cf = cryptfile.CryptFile()
  cf.set_key_with_psk('MYPASSWORDFORFILECRYPT')

  linear_regression_prepare_inputs_and_transmit_no_offload('data', mode, cf, he) 

  print("Indirectly invoke lambda ...")
  #os.system('./invoke.sh')
  message = {}
  message['app'] = 'linear_regression'
  #client_for_awsiot.publish(message)

  # wait return
  while 1:
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit()

def linear_regression_offload(mode, client_for_proxy):
  if mode == 'he-wp' or mode == 'he-pp':
    print("he offload")
  elif mode == 'se-wp' or mode == 'se-pp':
    print("se offload")
  else:
    print("[Client] Wrong mode")
    sys.exit()
    
  client_for_proxy.send_file("data/", "playground/input_data/video_small.mp4")

  with open('data/output.json') as jsonf:
    data = json.load(jsonf)
    print(data["body"])
    results = data["body"]
    if ENC_MODE == "noenc":
      for i, res in enumerate(results):
        r = np.loadtxt("data/res." + str(i) + ".out")
        print(r)
    else:
      for i, res in enumerate(results):
        r = wrapper.Ciphertext()
        r.load("data/res." + str(i) + ".out")
        print(he.decryptor_decoder(r))
