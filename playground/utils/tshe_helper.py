#from ..tensorslow_he import operator
import numpy as np

class TensorslowHeHelper():
  def __init__(self, heal):
    self.heal = heal
  
  def list2array(self, l):
    encrypted_l = []
      
    if (len(l.shape)) == 1:
      encrypted_l = self.heal.encryptor_encoder.encode(l)

    elif (len(l.shape)) == 2:
      for i in range(0,len(l)):
        dot = self.heal.encryptor_encoder.encode(l[i])
        encrypted_l.append(dot)
          
    return np.asarray(encrypted_l)
