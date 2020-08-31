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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

ENC_MODE="enc" # "enc" or "noenc"

# global vars.
s3 = S3(isClient=True, isLocal=False)
global tx_start
global total_start
tx_start = 0
total_start = 0

#global client_for_proxy
#client_for_proxy = None
global ready_to_go
ready_to_go = False

# Run on client (he-d, se-d modes only)
# This callback prints performance results from the lambda
def cryptonets_callback(client, userdata, message):
  # Download results
  #s3.download_file('selcrypt', 'all_outputs.zip', 'data/all_outputs.zip')
  s3.download_and_extract('selcrypt', 'all_outputs.zip', 'data/all_outputs.zip')
  
  global tx_start
  global total_start
  arrival_time = time.time()
  total_diff = arrival_time - total_start
  print("[Client] Received a new message (from awsiot): ")
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}" + message.payload.decode() + f"{bcolors.ENDC}")
  print("[Client] from topic: ")
  print(message.topic)
  tx_diff = arrival_time - tx_start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] Tx time {tx_diff*1000} ms{bcolors.ENDC}")
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] Total time {total_diff*1000} ms{bcolors.ENDC}")
  print("--------------\n")

# Run on client (he-wp, he-pp, se-wp, se-pp modes only)
def cmd_proxy_ready(arg, mode):
  #global client_for_proxy
  print("[Client] Got a ready signal")
  global ready_to_go
  ready_to_go = True

# Run on client (he-wp, he-pp, se-wp, se-pp modes only)
def cmd_proxy_return(arg, mode):
  # Download results
  #s3.download_file('selcrypt', 'all_outputs.zip', 'data/all_outputs.zip')
  s3.download_and_extract('selcrypt', 'all_outputs.zip', 'data/all_outputs.zip')

  print("[Client] Got a return from proxy")
  global tx_start
  global total_start
  arrival_time = time.time()
  total_diff = arrival_time - total_start
  tx_diff = arrival_time - tx_start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] Tx time {tx_diff*1000} ms{bcolors.ENDC}")
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] Total time {total_diff*1000} ms{bcolors.ENDC}")
  print("--------------\n")

# Run on client
def cryptonets_inputs(destdir, enc_mode, he=None):
  x1 = 15
  print("Generating pseudo-weights for Conv 1 ...\n")
  p_conv_len = 5*25
  p_conv_vec = [5 for _ in range(0, p_conv_len)]
  if enc_mode == "enc":
    p_conv_vec = he.plaintext_encoder.encode(p_conv_vec)

  c_conv_len = x1*25
  c_conv_vec = [3 for _ in range(0, c_conv_len)]
  if enc_mode == "enc":
    c_conv_vec = he.encryptor_encoder.encode(c_conv_vec)
  
  print("Generating pseudo-weights for Pool ...\n")
  p_pool_len = 100*5*x1
  p_pool_vec = [6 for _ in range(0, p_pool_len)]
  if enc_mode == "enc":
    p_pool_vec = he.plaintext_encoder.encode(p_pool_vec)

  print("Generating pseudo-weights for FC ...\n")
  p_fc_len = 10*100
  p_fc_vec = [9 for _ in range(0, p_fc_len)]
  if enc_mode == "enc":
    p_fc_vec = he.plaintext_encoder.encode(p_fc_vec)

  print("...pseudo-weights for Conv 1, Pool and FC complete\n")
  for i in range(0, p_conv_len):
    if enc_mode == "noenc":
      np.savetxt(os.path.join(destdir, "p_conv_vec." + str(i) + ".in"), [p_conv_vec[i]], fmt='%i')
    else:
      p_conv_vec[i].save(os.path.join(destdir, "p_conv_vec." + str(i) + ".in"))
  for i in range(0, c_conv_len):
    if enc_mode == "noenc":
      np.savetxt(os.path.join(destdir, "c_conv_vec." + str(i) + ".in"), [c_conv_vec[i]],fmt='%i')
    else:
      c_conv_vec[i].save(os.path.join(destdir, "c_conv_vec." + str(i) + ".in"))
  for i in range(0, p_pool_len):
    if enc_mode == "noenc":
      np.savetxt(os.path.join(destdir, "p_pool_vec." + str(i) + ".in"), [p_pool_vec[i]],fmt='%i')
    else:
      p_pool_vec[i].save(os.path.join(destdir, "p_pool_vec." + str(i) + ".in"))
  for i in range(0, p_fc_len):
    if enc_mode == "noenc":
      np.savetxt(os.path.join(destdir, "p_fc_vec." + str(i) + ".in"), [p_fc_vec[i]],fmt='%i')
    else:
      p_fc_vec[i].save(os.path.join(destdir, "p_fc_vec." + str(i) + ".in"))

# Run on client
def cryptonets_prepare_inputs_no_offload(destdir, mode, cf, he):

  if mode[:2] == 'he':
    enc_start = time.time()
    cf.encrypt_file_with_he(destdir, 'playground/input_data/video_small.mp4', he)
    #cf.encrypt_file_with_he(destdir, 'playground/input_data/image_tiny.png', he)
    print("[Client] Zipping encrypted video_small.mp4 as a name video_small.mp4")
    os.system('cd {} && zip -q -r video_small.mp4 video_small.mp4.*.enc && rm video_small.mp4.*.enc && cd -'.format(destdir))
  elif mode[:2] == 'se':
    aes_start = time.time()
    cf.encrypt_file(destdir, 'playground/input_data/video_small.mp4')
    aes_diff = time.time() - aes_start
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] AES Encrypt: done in {aes_diff*1000} ms{bcolors.ENDC}")
    enc_start = time.time()
  else:
    print("[Client] Wrong mode")
    sys.exit()
  
  cryptonets_inputs(destdir, "enc", he)
  
  enc_diff = time.time() - enc_start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] HE Encrypt and Save: done in {enc_diff*1000} ms{bcolors.ENDC}")

def cryptonets_transmit_inputs_no_offload(destdir):
  # Zip all and send them at once
  os.system("cd {} && zip -q -r all_inputs.zip . && cd -".format(destdir))
  s3.upload_file('{}/all_inputs.zip'.format(destdir), 'selcrypt', 'all_inputs.zip')

# Run on proxy
def cryptonets_inputs_offloaded(target_data, mode, he):
  destdir = os.path.dirname(target_data)
  print("[Proxy] Unzipping {}...".format(target_data))
  os.system("unzip -o -q {} -d {}".format(target_data, destdir))
  x1 = 15
  print("Generating pseudo-weights for Conv 1 ...\n")
  p_conv_len = 5*25
  p_conv_vec = []
  for i in range(p_conv_len):
    with open(os.path.join(ROOT_DIR,destdir,"p_conv_vec.{}.in".format(i))) as fi:
      p_conv_vec.append(int(fi.read()))
  p_conv_vec = he.plaintext_encoder.encode(p_conv_vec)

  c_conv_len = x1*25
  c_conv_vec = []
  for i in range(c_conv_len):
    with open(os.path.join(ROOT_DIR,destdir,"c_conv_vec.{}.in".format(i))) as fi:
      c_conv_vec.append(int(fi.read()))
  c_conv_vec = he.encryptor_encoder.encode(c_conv_vec)
  
  print("Generating pseudo-weights for Pool ...\n")
  p_pool_len = 100*5*x1
  p_pool_vec = []
  for i in range(p_pool_len):
    with open(os.path.join(ROOT_DIR,destdir,"p_pool_vec.{}.in".format(i))) as fi:
      p_pool_vec.append(int(fi.read()))
  p_pool_vec = he.plaintext_encoder.encode(p_pool_vec)

  print("Generating pseudo-weights for FC ...\n")
  p_fc_len = 10*100
  p_fc_vec = []
  for i in range(p_fc_len):
    with open(os.path.join(ROOT_DIR,destdir,"p_fc_vec.{}.in".format(i))) as fi:
      p_fc_vec.append(int(fi.read()))
  p_fc_vec = he.plaintext_encoder.encode(p_fc_vec)

  print("...pseudo-weights for Conv 1, Pool and FC complete\n")
  for i in range(0, p_conv_len):
    p_conv_vec[i].save(os.path.join(ROOT_DIR,destdir, "p_conv_vec." + str(i) + ".in"))
  for i in range(0, c_conv_len):
    c_conv_vec[i].save(os.path.join(ROOT_DIR,destdir, "c_conv_vec." + str(i) + ".in"))
  for i in range(0, p_pool_len):
    p_pool_vec[i].save(os.path.join(ROOT_DIR,destdir, "p_pool_vec." + str(i) + ".in"))
  for i in range(0, p_fc_len):
    p_fc_vec[i].save(os.path.join(ROOT_DIR,destdir, "p_fc_vec." + str(i) + ".in"))

# Run on proxy
def cryptonets_prepare_inputs_offloaded(target_data, mode, cf, he):
  destdir = os.path.dirname(target_data)

  if mode[:2] == 'he':
    enc_start = time.time()
    cf.encrypt_file_with_he(destdir, 'playground/input_data/video_small.mp4', he)
    #cf.encrypt_file_with_he(destdir, 'playground/input_data/image_tiny.png', he)
    print("[Proxy] Zipping encrypted video_small.mp4 as a name video_small.mp4")
    os.system('cd {} && zip -q -r video_small.mp4 video_small.mp4.*.enc && rm video_small.mp4.*.enc && cd -'.format(destdir))
  elif mode[:2] == 'se':
    aes_start = time.time()
    cf.encrypt_file(destdir, 'playground/input_data/video_small.mp4')
    aes_diff = time.time() - aes_start
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Proxy] AES Encrypt: done in {aes_diff*1000} ms{bcolors.ENDC}")
    enc_start = time.time()
  else:
    print("[Proxy] Wrong mode")
    sys.exit()
  
  cryptonets_inputs_offloaded(target_data, mode, he)
  
  enc_diff = time.time() - enc_start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Proxy] HE Encrypt and Save: done in {enc_diff*1000} ms{bcolors.ENDC}")
  
# Run on proxy
def cryptonets_transmit_inputs_offloaded(destdir):
  # Zip all and send them at once
  print("[Proxy] Zipping all the prepared inputs as all_inputs.zip")
  os.system("cd {} && zip -q -r all_inputs.zip . && cd -".format(destdir))
  print("[Proxy] Transmit all_inputs.zip to aws iot")
  s3.upload_file('{}/all_inputs.zip'.format(destdir), 'selcrypt', 'all_inputs.zip')
  
# Run on client
def cryptonets_transmit_plain_inputs_offload(srcdir, proxy_destdir, mode, client_for_proxy):
  # Gen inputs and save them locally as plaintext
  cryptonets_inputs(srcdir, "noenc")

  # Zip all 
  print("[Client] Zipping all the plain inputs for offloading")
  os.system('cd {} && zip -q -r all_plain_inputs.zip . && cd -'.format(srcdir))
  
  global tx_start
  tx_start = time.time()
  # transmit inputs
  print("[Client] Transmit all_plain_inputs.zip to proxy")
  client_for_proxy.send_file(proxy_destdir, os.path.join(srcdir,"all_plain_inputs.zip"))
  #client_for_proxy.send_file(destdir, os.path.join(destdir,"p_pool_vec.1.in"))

# Run on client
def cryptonets_no_offload(mode, client_for_awsiot, _total_start):
  global total_start
  total_start = _total_start
  client_for_awsiot.connect_and_subscribe(cryptonets_callback)
  start = time.time()
  # he init
  poly_modulus = 1 << 12
  coeff_modulus = 1 << 13
  plain_modulus = 1099511922689
  #plain_modulus = 786433
  he = ph(poly_modulus, coeff_modulus, plain_modulus)
  he.saveParmsAndKeys("data/"); # data/seal.parms, data/pub.key
  diff = time.time() - start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] HE Init: done in {diff*1000} ms{bcolors.ENDC}")

  cf = cryptfile.CryptFile()
  cf.set_key_with_psk('MYPASSWORDFORFILECRYPT')

  cryptonets_prepare_inputs_no_offload('data', mode, cf, he) 
  
  global tx_start
  tx_start = time.time()

  cryptonets_transmit_inputs_no_offload('data') 

  print("[Client] Invoke lambda ...")
  #os.system('./invoke.sh')
  message = {}
  message['app'] = 'cryptonets'
  client_for_awsiot.publish(message)

  # wait return
  while 1:
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit()

# Run on client
def cryptonets_offload(mode, client_for_proxy, _total_start):
  global total_start
  total_start = _total_start

  client_for_proxy.set_cmd_callback("proxy_ready", cmd_proxy_ready)
  client_for_proxy.set_cmd_callback("proxy_return", cmd_proxy_return)
  # wait for a result (in json format)
  client_for_proxy.run()

  # Busy waiting for proxy ready.
  while True:
    if ready_to_go:
      break
    else:
      time.sleep(1)
  
  cryptonets_transmit_plain_inputs_offload('data', 'data_proxy', mode, client_for_proxy)

  client_for_proxy.send_cmd("crypto_offload", "data_proxy/all_plain_inputs.zip", mode)

  # wait return
  while 1:
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit()

def cryptonets_local(mode, _total_start):
  global total_start
  total_start = _total_start
  
  start = time.time()
  # he init
  poly_modulus = 1 << 12
  coeff_modulus = 1 << 13
  plain_modulus = 1099511922689
  #plain_modulus = 786433
  he = ph(poly_modulus, coeff_modulus, plain_modulus)
  he.saveParmsAndKeys("data/"); # data/seal.parms, data/pub.key
  diff = time.time() - start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client] HE Init: done in {diff*1000} ms{bcolors.ENDC}")

  cf = cryptfile.CryptFile()
  cf.set_key_with_psk('MYPASSWORDFORFILECRYPT')

  destdir = 'data'

  if mode[:2] == 'he':
    enc_start = time.time()
    cf.encrypt_file_with_he(destdir, 'playground/input_data/video_small.mp4', he)
    #cf.encrypt_file_with_he(destdir, 'playground/input_data/image_tiny.png', he)
    print("[Client-Local] Zipping encrypted video_small.mp4 as a name video_small.mp4")
    os.system('cd {} && zip -q -r video_small.mp4 video_small.mp4.*.enc && rm video_small.mp4.*.enc && cd -'.format(destdir))
  elif mode[:2] == 'se':
    aes_start = time.time()
    cf.encrypt_file(destdir, 'playground/input_data/video_small.mp4')
    aes_diff = time.time() - aes_start
    print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client-Local] AES Encrypt: done in {aes_diff*1000} ms{bcolors.ENDC}")
    enc_start = time.time()
  else:
    print("[Client-Local] Wrong mode")
    sys.exit()
  
  cryptonets_inputs(destdir, "enc", he)
  
  enc_diff = time.time() - enc_start
  print(f"{bcolors.BOLD}{bcolors.OKGREEN}@ [Client-Local] HE Encrypt and Save: done in {enc_diff*1000} ms{bcolors.ENDC}")

  print(f"{bcolors.BOLD}{bcolors.OKGREEN}[Client-local] Invoke lambda ...{bcolors.ENDC}")
  os.system('playground/invoke.sh')
  
