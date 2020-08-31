from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import sys, os

sys.path.append(os.path.dirname(sys.path[0]))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
  print("Received a new message: ")
  print(message.payload)
  print("from topic: ")
  print(message.topic)
  print("--------------\n\n")

class AWSIoT():
  def __init__(self, configfile):
    with open(configfile, 'r') as f:
      configs = json.load(f)
      self.host = configs['endpoint'] # required
      self.rootCAPath = os.path.join(ROOT_DIR,configs['rootCA']) # required
      self.certificatePath = os.path.join(ROOT_DIR,configs['cert'])
      self.privateKeyPath = os.path.join(ROOT_DIR,configs['key'])
      self.port = int(configs['port'])
      self.useWebsocket = True if configs['websocket'] == 'True' else False
      self.clientId = configs['clientId']
      self.pub_topic = configs['pub_topic']
      self.sub_topic = configs['sub_topic']
      self.mode = configs['mode']

    if self.mode not in AllowedActions:
      print("Unknown --mode option %s. Must be one of %s" % (self.mode, str(AllowedActions)))
      exit(2)

    if self.useWebsocket and self.certificatePath and self.privateKeyPath:
      print("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
      exit(2)

    if not self.useWebsocket and (not self.certificatePath or not self.privateKeyPath):
      print("Missing credentials for authentication.")
      exit(2)

    # Port defaults
    if self.useWebsocket and not self.port:  # When no port override for WebSocket, default to 443
      self.port = 443
    if not self.useWebsocket and not self.port:  # When no port override for non-WebSocket, default to 8883
      self.port = 8883

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.WARNING)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Init AWSIoTMQTTClient
    self.myAWSIoTMQTTClient = None
    if self.useWebsocket:
      self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId, useWebsocket=True)
      self.myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
      self.myAWSIoTMQTTClient.configureCredentials(self.rootCAPath)
    else:
      self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
      self.myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
      self.myAWSIoTMQTTClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)

    # AWSIoTMQTTClient connection configuration
    self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

  def connect_and_subscribe(self, callback_fn): 
    # Connect and subscribe to AWS IoT
    self.myAWSIoTMQTTClient.connect()
    if self.mode == 'both' or self.mode == 'subscribe':
      self.myAWSIoTMQTTClient.subscribe(self.sub_topic, 1, callback_fn)
    time.sleep(2)
  
  def publish(self, message):
    messageJson = json.dumps(message)
    self.myAWSIoTMQTTClient.publish(self.pub_topic, messageJson, 1)
    print('Published topic %s: %s\n' % (self.pub_topic, messageJson))
    time.sleep(1)
    
    # Publish to the same topic in a loop forever
    #loopCount = 0
    #while True:
    #  if args.mode == 'both' or args.mode == 'publish':
    #    message = {}
    #    message['message'] = args.message
    #    message['sequence'] = loopCount
    #    messageJson = json.dumps(message)
    #    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    #    if args.mode == 'publish':
    #      print('Published topic %s: %s\n' % (topic, messageJson))
    #    loopCount += 1
    #  time.sleep(1)
