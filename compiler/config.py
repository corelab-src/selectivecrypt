import json

class Config():
  def __init__(self, filename):
    try:
      with open(filename, 'r') as f:
        config = json.load(f)
        self.target_funcs = config['target_funcs']
        self.exceptional_uses = config['exceptional_uses']
        self.ciphertext_encode = config['ciphertext_encode']
        self.data_in = config['data_in']
        self.data_out = config['data_out']
        self.mode = config['mode']
    except IOError:
      print("Error: locate configuration file.")

  def dumpConfig(self):
    print("CONFIG: Target Functions")
    print(self.target_funcs)
    print("CONFIG: Uses witout processing")
    print(self.exceptional_uses)
    print("CONFIG: Ciphertext Encode")
    print(self.ciphertext_encode)
    print("CONFIG: receive function name")
    print(self.data_in)
    print("CONFIG: send function name")
    print(self.data_out)
    print("CONFIG: compile mode")
    print(self.mode)
