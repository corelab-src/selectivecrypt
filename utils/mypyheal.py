import os, json
from pyheal import wrapper
from pyheal import encoders

class MyPyHeal():
  def __init__(self, poly_modulus=0, coeff_modulus=0, plain_modulus=0,
               pubkey_path=None):
    scheme = 'BFV'
    self.poly_modulus = poly_modulus
    self.coeff_modulus = coeff_modulus
    self.plain_modulus = plain_modulus

    self.parms = wrapper.EncryptionParameters(scheme_type=scheme)

    if self.poly_modulus > 0 and self.coeff_modulus > 0 and self.plain_modulus > 0:
      self.parms.set_poly_modulus(self.poly_modulus)
      self.parms.set_coeff_modulus(wrapper.coeff_modulus_256(self.coeff_modulus))
  #    parms.set_coeff_modulus([wrapper.SmallModulus(1099511922689),wrapper.SmallModulus
  #        (1099512004609)])
      self.parms.set_plain_modulus(self.plain_modulus)
    
    seal_context_ = wrapper.Context(self.parms).context
    self.context = seal_context_
    
    if pubkey_path == None:
      self.keygen = wrapper.KeyGenerator(seal_context_)
    else:
      pub = wrapper.PublicKey()
      pub.load(pubkey_path)
      #sec = wrapper.SecretKey()
      #sec.load(seckey_path)
      #self.keygen = wrapper.KeyGenerator(seal_context_, sec, pub)
      self.keygen = wrapper.KeyGenerator(seal_context_, public=pub)
    self.evaluator = wrapper.Evaluator(ctx=seal_context_)
    self.plaintext_encoder = encoders.PlainTextEncoder(
      encoder=wrapper.FractionalEncoder(smallmod=wrapper.SmallModulus(self.plain_modulus),
        poly_modulus_degree=self.poly_modulus,
        integer_coeff_count=64,
        fraction_coeff_count=32,
        base=2)
    )
    self.encryptor_encoder = encoders.EncryptorOp(plaintext_encoder=self.plaintext_encoder,
      encryptor=wrapper.Encryptor(ctx=seal_context_, public=self.keygen.public_key()),
      evaluator=wrapper.Evaluator(ctx=seal_context_),
#                                             relin_key=self.keygen.relin_keys(decomposition_bit_count=16, count=2)
      relin_key=self.keygen.relin_keys(decomposition_bit_count=60, count=1)
    )
    if pubkey_path is None:
      self.decryptor_decoder = encoders.Decryptor(plaintext_encoder=self.plaintext_encoder,
        decryptor=wrapper.Decryptor(ctx=seal_context_, secret=self.keygen.secret_key())
      )
    else:
      self.decryptor_decoder = None
    self.batch_encoder = wrapper.BatchEncoder(self.context)
    print("MyPyHeal: context generated with n={}, q={}, t={}".format(self.poly_modulus, self.coeff_modulus, self.plain_modulus))

  def saveParmsAndKeys(self, destdir):
    parms_out = {"poly_modulus": self.poly_modulus,
      "coeff_modulus": self.coeff_modulus,
      "plain_modulus": self.plain_modulus}
    with open(os.path.join(destdir, 'seal.parms'), 'w') as f:
      json.dump(parms_out, f)
    
    pubkey = self.keygen.public_key()
    seckey = self.keygen.secret_key()
    relinkey = self.keygen.relin_keys(60, 1) # 16, 2
    pubkey.save(os.path.join(destdir, "pub.key"))
    seckey.save(os.path.join(destdir, "sec.key")) # temporary
    relinkey.save(os.path.join(destdir, "relin.key"))

