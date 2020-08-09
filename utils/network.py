# CLIENT CODE
# Update 1.1 AES Encryption Now Included :p
# AES Block Cipher 16 bytes block size as supported by pyaes
# Server Code Must Be Running Before Starting Client or Connection will be refused
# Author : xtreme.research@gmail.com

import os
try:
  import pyaes # run : $ pip install pyaes
except ImportError:
  print("Install pyaes library!")
  print("windows : python -m pip insatll pyaes")
  print("linux   : pip install pyaes ")
  exit()
import sys, time
import socket
from struct import pack, unpack
import threading
import hashlib
import json
from datetime import datetime
sys.path.append(os.path.dirname(sys.path[0]))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# common funcs
def process_bytes(bytess):
  ret = []
  while(len(bytess)>=16):
    if(len(bytess)>=16):
      byts = bytess[:16]
      ret.append(byts)
      bytess = bytess[16:]
    else:
      print("Block Size Mismatch ")
  return ret

def process_text(data): #take data in as a string return 16 bytes block of bytes list
  streams = []
  while (len(data)>0):
    if(len(data)>=16):
      stream = data[:16]
      data = data[16:]
    else:
      stream = data + ("~"*(16-len(data)))
      data = ''
    stream_bytes = [ ord(c) for c in stream]
    streams.append(stream_bytes)
  return streams

def verify_and_display(recv_dict):
  timestamp = recv_dict['timestamp']
  recv_hash = recv_dict['hash']
  message   = recv_dict['message']
  mess_hash = hashlib.sha256(str(message).encode('utf-8')).hexdigest()
  SET_LEN = 80
  if (mess_hash == recv_hash):
    tag = str('☑')
  else:
    tag = str('☒')
  spaces = SET_LEN - len(str(message)) - len('Received : ') - 1
  if spaces > 0 :
    space = ' '*spaces
    sentence = 'Received : ' + str(message) + space + tag + '  ' + timestamp
    print(sentence)

#def recv_cmd_handler(sock_or_conn, cmd_callbacks):
#  _lenmd = sock_or_conn.recv(8)
#  (lenmd,) = unpack('>Q', _lenmd)
#  md = sock_or_conn.recv(lenmd)
#  cmd = md.decode().split(":")
#  print(cmd) 
#  if len(cmd) != 2:
#    print("Wrong cmd transfer protocol")
#    exit()
#  eval(cmd_callbacks[cmd[0]])
"""
# Client's
def cmd_handler(sock_or_conn, cmd_callbacks):
  while True:
    try:
      _lenmd = sock_or_conn.recv(8)
      (lenmd,) = unpack('>Q', _lenmd)
      message = sock_or_conn.recv(lenmd)
      cmd_md = message.decode().split(":")

      if cmd_md[0] == "cmd":
        print("\n[Client] Got a cmd request:")
        if len(cmd_md) != 4:
          print("[Client] Wrong cmd transfer protocol")
          exit()
        # Temporary
        cmd = cmd_md[1]
        arg = cmd_md[2]
        mode = cmd_md[3]
        
        cmd_callbacks[cmd](arg, mode)
    except ConnectionResetError:
      print('[Client] Broken PIPE!')

# Client's
def recv_file_handler(sock_or_conn):
  _lenmd = sock_or_conn.recv(8)
  (lenmd,) = unpack('>Q', _lenmd)
  message = sock_or_conn.recv(lenmd)
  outpath_filename = message.decode().split(":")
  print(outpath_filename)
  if (len(outpath_filename) != 2):
    print("Wrong file transfer protocol")
    exit()
  outpath = outpath_filename[0]
  filename = outpath_filename[1]
  _lenfile = sock_or_conn.recv(8)
  (lenfile,) = unpack('>Q', _lenfile)
  
  rsize = 0
  with open(os.path.join(ROOT_DIR, outpath, filename), 'wb') as fo:
    data = sock_or_conn.recv(1024)
    while data:
      fo.write(data)
      rsize = rsize + len(data)
      data = sock_or_conn.recv(1024)
    if rsize != int(lenfile):
      print("rsize is {} (should be {})".format(rsize, lenfile))
      print("{} download failed.".format(filename))
      exit()
    print("{} downloaded in {}.".format(filename, outpath))
"""
def _send_cmd(sock_or_conn, cmd, arg, mode):
  md = ("cmd:"+cmd+":"+arg+":"+mode).encode()
  lenmd = pack('>Q', len(md))
  sock_or_conn.sendall(lenmd)
  sock_or_conn.sendall(md) 
  print("[{}] cmd sended with arg [{}] in [{}] mode.".format(cmd, arg, mode))

# Proxy and client
def recv_file_and_task_handler(sock_or_conn, cmd_callbacks):
  while True:
    try:
      _lenmd = sock_or_conn.recv(8)
      (lenmd,) = unpack('>Q', _lenmd)
      message = sock_or_conn.recv(lenmd)
      cmd_or_else = message.decode().split(":")

      if cmd_or_else[0] == "cmd":
        if len(cmd_or_else) != 4:
          print("[Client/Proxy] Wrong cmd transfer protocol")
          exit()
        # Temporary
        cmd = cmd_or_else[1]
        arg = cmd_or_else[2]
        mode = cmd_or_else[3]
        print("\n[Client/Proxy] Got a cmd request: cmd [{}] with arg [{}] and mode [{}]".format(cmd,arg,mode))
        
        cmd_callbacks[cmd](arg, mode)
      else:
        outpath_filename = cmd_or_else
        print("\n[Client/Proxy] Got a file recv request:")
        print(outpath_filename)
        if len(outpath_filename) != 2:
          print("[Client/Proxy] Wrong file transfer protocol")
          exit()
        outpath = outpath_filename[0]
        filename = outpath_filename[1]
        _lenfile = sock_or_conn.recv(8)
        (lenfile,) = unpack('>Q', _lenfile)
        
        rsize = 0
        with open(os.path.join(ROOT_DIR, outpath, filename), 'wb') as fo:
          data = sock_or_conn.recv(1024 if lenfile-rsize >= 1024 else lenfile-rsize)
          while data:
            fo.write(data)
            rsize = rsize + len(data)
            data = sock_or_conn.recv(1024 if lenfile-rsize >= 1024 else lenfile-rsize)
          if rsize != int(lenfile):
            print("[Client/Proxy] rsize is {} (should be {})".format(rsize, lenfile))
            print("[Client/Proxy] {} download failed.".format(filename))
            exit()
          print("[Client/Proxy] {} downloaded in {}.".format(filename, outpath))
    except ConnectionResetError:
      print('[Client/Proxy] Broken PIPE!')
    except KeyboardInterrupt:
      sys.exit()

def _send_file(sock_or_conn, outpath, filename):
  size = os.path.getsize(os.path.join(ROOT_DIR,filename))
  with open(filename, "rb") as fi:
    md = (outpath+":"+os.path.basename(filename)).encode()
    lenmd = pack('>Q', len(md)) # for endian-free
    lenfile = pack('>Q', size)
    sock_or_conn.sendall(lenmd)
    sock_or_conn.sendall(md)
    sock_or_conn.sendall(lenfile)
    
    while 1:
      data = fi.read(1024)
      sock_or_conn.send(data)
      if not data:
        break
    fi.close()
    print("{} sended to {}.".format(filename, outpath))

class Client():
  def __init__(self, psk):
    print("[+] Client Running ")
    #HOST = str(input('[+] Enter Destination IP   : '))
    #PORT = int(input('[+] Enter Destination Port : '))
    #key = str(input('[+] AES Pre-Shared-Key For Connection :'))
    key = psk
    hashed = hashlib.sha256(key.encode()).digest()
    self.aes = pyaes.AES(hashed)
    
    self.cmd_callbacks = {}

  def set_cmd_callback(self, cmd, callback):
    self.cmd_callbacks[cmd] = callback
    print("[Client] command callback [{}] registered.".format(callback.__name__))
  
  def setConnection(self, ip, port):
    print("[+] Try to set connection to ... {}, {}".format(ip, port))
    HOST = ip
    PORT = port
    try:
      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.s.connect((HOST, PORT))
    except ConnectionError:
      print('Could Not Connect !')
      exit(-1)

  def send_file(self, outpath, filename):
    _send_file(self.s, outpath, filename) 
  
  def send_cmd(self, cmd, arg, mode):
    _send_cmd(self.s, cmd, arg, mode) 
  
  def run(self): # client
#    Listening_Thread = myThread(1, self.conn, self.aes)
#    Listening_Thread.daemon = True
#    Listening_Thread.start()
    ListeningThread = threading.Thread(target=recv_file_and_task_handler, args=(self.s,self.cmd_callbacks,))
    ListeningThread.daemon = True
    ListeningThread.start()
    #ListeningThread.join()

class Proxy():
  def __init__(self, open_port, psk):
    HOST = '0.0.0.0'
    PORT = open_port 

    print("[+] Server Running ")
    print("[+] Allowing All Incoming Connections ")
    print("[+] PORT "+str(PORT))
    print("[+] Waiting For Connection...")

    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind((HOST, PORT))
    self.s.listen(1)
    self.conn, self.addr = self.s.accept()
    print('[+] Connected by ', self.addr)

    #key = str(input('[+] AES Pre-Shared-Key for the Connection : '))
    key = psk
    hashed = hashlib.sha256(key.encode()).digest()
    self.aes = pyaes.AES(hashed)
    
    self.cmd_callbacks = {}

  def set_cmd_callback(self, cmd, callback):
    self.cmd_callbacks[cmd] = callback
    print("[Proxy] command callback [{}] registered.".format(callback.__name__))
  
  def send_file(self, outpath, filename):
    _send_file(self.conn, outpath, filename) 
  
  def send_cmd(self, cmd, arg, mode):
    _send_cmd(self.conn, cmd, arg, mode) 

  def run(self):
#    Listening_Thread = myThread(1, self.conn, self.aes)
#    Listening_Thread.daemon = True
#    Listening_Thread.start()
    self.RecvFileThread = threading.Thread(target=recv_file_and_task_handler, args=(self.conn, self.cmd_callbacks,))
    self.RecvFileThread.daemon = True
    self.RecvFileThread.start()

  def wait(self):
    self.RecvFileThread.join()
        
    #RecvCmdThread = threading.Thread(target=recv_cmd_handler, args=(self.conn,))
    #RecvCmdThread.daemon = True
    #RecvCmdThread.start()
    #RecvFileThread.join()
    #RecvCmdThread.join()
  
