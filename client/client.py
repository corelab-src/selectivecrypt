import sys, os, time
import json
sys.path.append(os.path.dirname(sys.path[0]))
from utils.common import *
from utils.mypyheal import MyPyHeal as ph
from pyheal import wrapper
import utils.network as net
import utils.cryptfile as cryptfile
import utils.awsiot as awsiot
from benchmarks.cryptonets_client import *
from benchmarks.linear_regression_client import *

"""
Macro-Benchmark:
* cryptonets
* linear_regression
* logistic_regression
* perceptron
* mlp (multi layer perceptron)

Micro-Benchmark:
* average
* matmul
* dot

Macro Eval Mode:
* he-d: HE on device w/o proxy
* he-wp: HE w/ weak proxy
* he-pp: HE w/ powerful proxy
* se-d: SE on device w/o proxy
* se-wp: SE w/ weak proxy
* se-pp: SE w/ powerful proxy

* he-local: HE locally
* se-local: SE locally

Micro Eval Mode:
* d: on device 
* p: on proxy

Input Data (playground/input_data):
* cryptonets
  - cryptonets_data_he.txt
  - cryptonets_data_se.txt
* linear_regression
  - linear_regression_data_he.txt
  - linear_regression_data_se.txt
* logistic_regression
  - logistic_regression_data_he.txt
  - logistic_regression_data_se.txt
* perceptron
  - perceptron_data_he.txt
  - perceptron_data_se.txt 

Micro Input Data (playground/input_data):
* average
  - playground/input_data/average
* mm
  - playground/input_data/mmdot
* dot
  - playground/input_data/mmdot

@@ Why not non-encryption eval?
@@ video, image exchange
@@ Why not decode + decrypt eval?

Execution Time Evaluation (w/o proxy)
* Total execution time
* Setup time (init)
  - HE init
* Encryption time
  - HE (+AES) Encryption time
* Device-Proxy communication time
  - 0
* Cloud communication time
  - cloud comp - Tx (client)
* Cloud computation time

Execution Time Evaluation (w/ proxy)
* Total execution time
* Setup time (init)
  - HE init (proxy)
* Encryption time
  - HE (+AES) Encryption time (proxy)
* Device-Proxy communication time
  - Total (proxy) - Tx (client)
* Cloud communication time
  - cloud comp - Tx (proxy)
* Cloud computation time
"""
logger = logging.getLogger("CLIENT")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# helper function
# Proxy Offload Mode: client (IoT Device) sends plaintext to proxy 
# and receive plaintext results. Proxy will do cryptographic tasks.
def isProxyOffloadMode(mode):
  if mode == 'he-d' or \
     mode == 'se-d' or \
     mode == 'd':
    return False
  return True

def benchmark_wrapper(benchmark, mode, total_start):
  os.system("find data/ ! -name 'README.md' -type f -exec rm {} +")
  
  if mode[3:] == "local":
    if benchmark == 'cryptonets':
      cryptonets_local(mode, total_start)
    elif benchmark == 'linear_regression':
      return
    return

  if not isProxyOffloadMode(mode):
    # 0. connect to aws
    # 1. keygen and save
    # 2. prepare inputs (encryption)
    # 3. send them to s3 directly
    # 4. publish a topic (invoke lambda)
    # 5. wait returns from lambda
    client_for_awsiot = awsiot.AWSIoT('playground/awsiot.client.config.json')
    if benchmark == 'cryptonets':
      cryptonets_no_offload(mode, client_for_awsiot, total_start)
    elif benchmark == 'linear_regression':
      linear_regression_no_offload(mode, client_for_awsiot, total_start)
  else:
    logger.info("Offload to proxy")
    # 0. connect to proxy
    # 1. send inputs to proxy as plaintexts
    # 2. wait returns from proxy
    client_for_proxy = net.Client('MYPASSWORD')
    client_for_proxy.setConnection('127.0.0.1', 8080)

    if benchmark == 'cryptonets':
      cryptonets_offload(mode, client_for_proxy, total_start)
    elif benchmark == 'linear_regression':
      linear_regression_offload(mode, client_for_proxy, total_start)

def main(argv):
  total_start = time.time()
  if len(argv) != 3:
    logger.warning(f"Usage:")
    logger.warning(f"python client.py [benchmark] [eval_mode]")
    sys.exit()
  BENCHMARK = argv[1]
  EVAL_MODE = argv[2] 
  logger.debug(f"Evaluate [{BENCHMARK}] with [{EVAL_MODE}] mode.")
  benchmark_wrapper(BENCHMARK, EVAL_MODE, total_start)

if __name__ == "__main__":
  main(sys.argv)
