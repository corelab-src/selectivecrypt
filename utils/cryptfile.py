from Crypto import Random
from Crypto.Cipher import AES
import json
import hashlib
import os
import struct
import numpy as np
from pyheal import wrapper
from pyheal import ciphertext_op

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def pad(s):
  return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
  message = pad(message)
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
  iv = ciphertext[:AES.block_size]
  cipher = AES.new(key, AES.MODE_CBC, iv)
  plaintext = cipher.decrypt(ciphertext[AES.block_size:])
  return plaintext.rstrip(b"\0")

def _encrypt_file(file_name, key):
  with open(file_name, 'rb') as fo:
    plaintext = fo.read()
  enc = encrypt(plaintext, key)
  return enc

def _decrypt_file(file_name, key):
  with open(file_name, 'rb') as fo:
    ciphertext = fo.read()
  dec = decrypt(ciphertext, key)
  return dec

def bytes2int(str):
 return int(str.encode('hex'), 16)

def bytes2hex(str):
 return '0x'+str.encode('hex')

def int2bytes(i):
 h = int2hex(i)
 return hex2bytes(h)

def int2hex(i):
 return hex(i)

def hex2int(h):
 if len(h) > 1 and h[0:2] == '0x':
  h = h[2:]
 if len(h) % 2:
  h = "0" + h
 return int(h, 16)

def hex2bytes(h):
 if len(h) > 1 and h[0:2] == '0x':
  h = h[2:]
 if len(h) % 2:
  h = "0" + h
 return h.decode('hex')

# wrapper class
class CryptFile():
  def __init__(self):
    self.key = ""

  def set_key_with_psk(self, psk):
    self.key = hashlib.sha256(psk.encode()).digest()
  
  def set_key(self, key):
    self.key = key

  def encrypt_file(self, output_path, file_name):
    if self.key == "":
      print("Please set a key first using 'set_key_with_psk'")
      exit()
    enc = _encrypt_file(file_name, self.key)
    with open(os.path.join(ROOT_DIR, output_path, os.path.basename(file_name) + ".enc"), 'wb') as fo:
      fo.write(enc)
    print("{} encrypted.".format(file_name))
  
  def decrypt_file(self, output_path, file_name):
    if self.key == "":
      print("Please set a key first using 'set_key_with_psk'")
      exit()
    dec = _decrypt_file(file_name, self.key)
    with open(os.path.join(ROOT_DIR, output_path, os.path.basename(file_name)[:-4]), 'wb') as fo:
      fo.write(dec)
    print("{} decrypted.".format(file_name))

  def encrypt_file_with_he(self, output_path, file_name, he):
    with open(os.path.join(ROOT_DIR,file_name), 'rb') as fi:
      content_text = str(fi.read()).encode().decode()
      content_ints = [ord(c) for c in content_text]
      
      #content_ints = struct.unpack(">I", content_bytes)[0]
      slot_count = he.batch_encoder.slot_count()
      split_cnt = len(content_ints) // slot_count \
                  if len(content_ints) % slot_count == 0 \
                  else len(content_ints) // slot_count + 1
      vecs = []
      i = 0
      while (i < split_cnt):
        if i*slot_count+slot_count < len(content_ints):
          vecs.append(content_ints[i*slot_count:i*slot_count+slot_count])
        else:
          vecs.append(content_ints[i*slot_count:len(content_ints)])
        i += 1
      encrypted_vec = []
      for i, vec in enumerate(vecs):
        encoded = he.batch_encoder.encode(vec)
        encrypted = he.encryptor_encoder.encode(encoded)
        encrypted.save(os.path.join(ROOT_DIR, output_path, os.path.basename(file_name) + '.' + str(i) + '.enc'))
        encrypted_vec.append(encrypted)
  
  # Currently out of range error on decoding batch encoded.
  def decrypt_file_with_he(self, output_path, file_name, he):
    c = wrapper.Ciphertext()
    c = ciphertext_op.CiphertextOp(ciphertext=c, evaluator=he.evaluator,
        plaintext_encoder=he.plaintext_encoder)
    c.load(file_name)
    decoded = he.decryptor_decoder.decode(c)
    print(decoded)
    

#key = b'\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18'
#pw_data = json.loads('../key.json')
#pw = pw_data["aes_password"]
#key = hashlib.sha256(pw.encode()).digest()

#encrypt_file('to_enc.txt', key)
#decrypt_file('to_enc.txt.enc', key)
