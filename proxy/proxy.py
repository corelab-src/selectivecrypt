import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from utils.common import *
import utils.network as net
import utils.cryptfile as cryptfile
import utils.awsiot as awsiot

logger = logging.getLogger("PROXY")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

import benchmarks.cryptonets_client as cryptonets_client
from benchmarks.linear_regression_client import *

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

global proxy 
global proxyworker 
proxy = None
proxyworker = None

global proxy_tx_start
global proxy_total_start
proxy_tx_start = 0
proxy_total_start = 0

def proxyworker_callback(client, userdata, message):
  global proxy_tx_start
  global proxy_total_start
  arrival_time = time.time()
  proxy_tx_diff = arrival_time - proxy_tx_start
  proxy_total_diff = arrival_time - proxy_total_start
  logger.info(f"from topic: {message.topic}")
  logger.debug(f"[Perf] Received a new message (from awsiot): {message.payload.decode()}")
  logger.debug(f"[Perf] Tx time {proxy_tx_diff*1000} ms")
  logger.debug(f"[Perf] Total time {proxy_total_diff*1000} ms")

  # send to client
  proxy.send_cmd("proxy_return", "", "")

class ProxyWorker():
  def __init__(self):
    self.client_for_awsiot = awsiot.AWSIoT(os.path.join(ROOT_DIR,'playground/awsiot.proxy.x86.config.json'))
    self.client_for_awsiot.connect_and_subscribe(proxyworker_callback)
    
    init_start = time.time()
    # he init
    poly_modulus = 1 << 12
    coeff_modulus = 1 << 13
    plain_modulus = 1099511922689
    #plain_modulus = 786433
    self.he = ph(poly_modulus, coeff_modulus, plain_modulus)
    self.he.saveParmsAndKeys(os.path.join(ROOT_DIR,"data_proxy/")); # data/seal.parms, data/pub.key
    init_diff = time.time() - init_start
    logger.debug(f"[Perf] HE Init: done in {init_diff*1000} ms")
  
    self.cf = cryptfile.CryptFile()
    self.cf.set_key_with_psk('MYPASSWORDFORFILECRYPT')

def cmd_crypto_offload(target_data, mode):
  logger.info(f"cmd_crypto_offload called.")
  logger.info(f"target_data: {target_data}")
  logger.info(f"mode: {mode}")
 
  destdir = os.path.dirname(target_data)

  global proxyworker
  cryptonets_client.cryptonets_prepare_inputs_offloaded(target_data, mode, proxyworker.cf, proxyworker.he)
  
  global proxy_tx_start
  proxy_tx_start = time.time()
  cryptonets_client.cryptonets_transmit_inputs_offloaded(destdir)
  
  logger.info(f"Invoke lambda ...")
  #os.system('./invoke.sh')
  message = {}
  message['app'] = 'cryptonets'
  proxyworker.client_for_awsiot.publish(message)
  
  # wait return
  while 1:
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit()
    
def main(argv):
  os.system("find data_proxy/ ! -name 'README.md' -type f -exec rm {} +")
  global proxy
  proxy = net.Proxy(8080, "MYPASSWORD")
  proxy.set_cmd_callback("crypto_offload", cmd_crypto_offload)
  logger.info("Run Proxy")
  proxy.run()
  
  global proxyworker
  proxyworker = ProxyWorker()
  
  global proxy_total_start
  proxy_total_start = time.time()
  proxy.send_cmd("proxy_ready", "", "")

  proxy.wait()

if __name__ == "__main__":
  main(sys.argv)
