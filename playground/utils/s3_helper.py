from pyheal import wrapper
from pyheal import ciphertext_op
import os
import numpy as np
try:
  import boto3
  import tempfile
  import zipfile
  from concurrent import futures
  from io import BytesIO
except ImportError:
  pass

class S3():
  def __init__(self, isClient=False, isLocal=False):
    self.isClient = isClient
    self.isLocal = isLocal
    if not isLocal and isClient:
      self.s3 = boto3.client('s3')

  def download_file(self, bucket, key, filename):
    print("s3: downloading a file from " + bucket + "/" + key + " as " + filename)
    if self.isLocal:
      os.system("cp " + bucket + "/" + key + " " + filename)
    else:
      if not self.isClient:
        self.s3.download_file(bucket, key, filename)
      else:
        os.system("aws s3 cp s3://" + bucket + "/" + key + " " + filename)
    
  def upload_file(self, filename, bucket, key):
    print("s3: uploading {} as {}/{}".format(filename,bucket,key))
    if self.isLocal:
      os.system("mkdir -p " + bucket)
      os.system("cp " + filename + " " + bucket + "/")
    else:
      if not self.isClient:
        self.s3.upload_file(filename, self.bucket, key)
      else:
        os.system("aws s3 cp " + filename + " s3://" + bucket + "/")

  def download_obj_local(self, bucket, key):
    print("S3: downloading an object from " + bucket + "/" + key)
#    with open(bucket + "/" + key, "r") as f:
#      data = f.read()
#      matrix = [item.split() for item in data.split('\n')[:-1]]
#      if (len
    data = np.loadtxt(bucket + "/" + key)
    return data
      
  def upload_obj_local(self, obj, bucket, key):
    print("S3: uploading object as " + bucket + "/" + key)
    os.system("mkdir -p " + bucket)
    if isinstance(obj, ciphertext_op.CiphertextOp) or \
       isinstance(obj, wrapper.Ciphertext) or \
       isinstance(obj, wrapper.Plaintext):
      obj.save(bucket + "/" + key)
    else:
      with open(bucket + "/" + key, "w") as f:
        if isinstance(obj, list):
          for line in obj:
            np.savetxt(f, line)
        else:
          np.savetxt(f, np.array([obj]))
#      f.write(str(obj))
#      f.close()
#    os.system("cp /tmp/" + key + " " + bucket + "/")

  # This is wrapper for download_file. 
  # It returns the file content as an object
  # to be trackable by compiler
  def download_obj(self, bucket, key, filename):
    self.download_file(bucket, key, filename)
    with open(filename, 'rb') as fi:
      content = fi.read()
      return content

  # This is wrapper for upload_file. 
  def upload_obj(self, obj, filename, bucket, key):
    self.upload_file(filename, bucket, key)
  
  # [Run on Lambda] 
  def extract_each(self, bucket, path, filename, zipdata):
    upload_status = 'success'
    try:
      self.s3.upload_fileobj(
        BytesIO(zipdata.read(filename)),
        bucket,
        os.path.join(path, filename)
      )
    except Exception:
      upload_status = 'fail'
    finally:
      return filename, upload_status

  # [Run on Lambda] Download zip file in memory and upload to s3
  def extract_and_upload(self, bucket, zipfilename):
    temp_file = tempfile.mktemp()
    self.s3.download_file(bucket, zipfilename, temp_file)
    zipdata = zipfile.ZipFile(temp_file)
    for filename in zipdata.namelist():
      n, res = self.extract_each(bucket, '', filename, zipdata)

  # [Run on Client]
  def download_and_extract(self, bucket, key, filename):
    self.s3.download_file(bucket, key, filename)
    with zipfile.ZipFile(filename, 'r') as zf:
      zf.extractall(os.path.dirname(filename))
      zf.close()
    #zipfile.ZipFile(filename).extractall(os.path.dirname(filename))

  # [Run on Lambda]
  def compress_and_upload(self, bucket, file_list, zipfilename):
    with zipfile.ZipFile(os.path.join("/tmp",zipfilename), "w") as zf:
      for f in file_list:
        zf.write(f, os.path.basename(f))
      zf.close()
      self.s3.upload_file(os.path.join("/tmp",zipfilename), bucket, zipfilename)
