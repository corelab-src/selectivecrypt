#from ..tensorslow_he import operator
import numpy as np

#class TensorslowHelper():
class helper():
  def __init__(self, heal=None):
    if heal is not None:
      self.heal = heal
    else:
      self.heal = None # Non-enc version

  def list2array(self, l):
    ret_l = []
      
    if (len(l.shape)) == 1:
      if self.heal is not None:
        ret_l = self.heal.encryptor_encoder.encode(l)
      else:
        ret_l = l

    elif (len(l.shape)) == 2:
      for i in range(0,len(l)):
        if self.heal is not None:
          dot = self.heal.encryptor_encoder.encode(l[i])
          ret_l.append(dot)
        else:
          ret_l.append(l[i])
          
    return np.asarray(ret_l)
