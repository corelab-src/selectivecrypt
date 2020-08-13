from utils.mypyheal import MyPyHeal as ph
from pyheal import wrapper
from pyheal import ciphertext_op
import time, json, os, sys
from utils.s3_helper import S3
s3 = S3()


def add_many(dots):
    dotsum = dots[0]
    for i in range(1, len(dots)):
        dotsum = dotsum + dots[i]
    return dotsum


def cryptonets():
    s3.download_file('selcrypt', 'seal.parms', '/tmp/seal.parms')
    s3.download_file('selcrypt', 'pub.key', '/tmp/pub.key')
    s3.download_file('selcrypt', 'relin.key', '/tmp/relin.key')
    with open('/tmp/seal.parms', 'r') as f:
        parms_in = json.load(f)
        heal = ph(poly_modulus=parms_in['poly_modulus'], coeff_modulus=
            parms_in['coeff_modulus'], plain_modulus=parms_in[
            'plain_modulus'], pubkey_path='/tmp/pub.key')
    plaintext_encoder = heal.plaintext_encoder
    encryptor_encoder = heal.encryptor_encoder
    evaluator = heal.evaluator
    x1 = 10
    p_conv_len = 5 * 25
    c_conv_len = x1 * 25
    p_conv_vec = []
    c_conv_vec = []
    for i in range(0, p_conv_len):
        s3.download_file('data', 'p_conv_vec.{}.in'.format(i),
            '/tmp/p_conv_vec.{}.in'.format(i))
        p = wrapper.Plaintext()
        p.load('/tmp/p_conv_vec.{}.in'.format(i))
        p_conv_vec.append(p)
    for i in range(0, c_conv_len):
        s3.download_file('data', 'c_conv_vec.{}.in'.format(i),
            '/tmp/c_conv_vec.{}.in'.format(i))
        c = wrapper.Ciphertext()
        c = ciphertext_op.CiphertextOp(ciphertext=c, evaluator=evaluator,
            plaintext_encoder=plaintext_encoder)
        c.load('/tmp/c_conv_vec.{}.in'.format(i))
        c_conv_vec.append(c)
    p_pool_len = 100 * 5 * x1
    p_pool_vec = []
    for i in range(0, p_pool_len):
        s3.download_file('data', 'p_pool_vec.{}.in'.format(i),
            '/tmp/p_pool_vec.{}.in'.format(i))
        po = wrapper.Plaintext()
        po.load('/tmp/p_pool_vec.{}.in'.format(i))
        p_pool_vec.append(po)
    p_fc_len = 10 * 100
    p_fc_vec = []
    for i in range(0, p_fc_len):
        s3.download_file('data', 'p_fc_vec.{}.in'.format(i),
            '/tmp/p_fc_vec.{}.in'.format(i))
        f = wrapper.Plaintext()
        f.load('/tmp/p_fc_vec.{}.in'.format(i))
        p_fc_vec.append(f)
    video = s3.download_obj('data', 'video.in')
    print('...Downloading inputs and weights is done\n')
    print('Calculating Conv 1 ...\n')
    dot_len = 25
    conv_out = []
    for i in range(0, p_conv_len, dot_len):
        for j in range(0, c_conv_len, dot_len):
            dots = []
            for x in range(0, dot_len):
                c_tpm = c_conv_vec[j + x] * p_conv_vec[i + x]
                dots.append(c_tpm)
            conv_out.append(add_many(dots))
    del p_conv_vec[:]
    del c_conv_vec[:]
    print(conv_out)
    print('...Conv 1 is done\n')
    print('Calculating activation layer 1 (square)...\n')
    act_out = []
    for i in range(0, len(conv_out)):
        c_tpm = conv_out[i] * conv_out[i]
        act_out.append(c_tpm)
    del conv_out[:]
    print(act_out)
    print('...Activation layer 1 is done\n')
    print('Calculating pool + linear...\n')
    dot_len = 5 * x1
    c_pool_len = 5 * x1
    pool_out = []
    for i in range(0, p_pool_len, dot_len):
        for j in range(0, c_pool_len, dot_len):
            dots = []
            for x in range(0, dot_len):
                c_tpm = act_out[j + x] * p_pool_vec[i + x]
                dots.append(c_tpm)
            pool_out.append(add_many(dots))
    del act_out[:]
    del p_pool_vec[:]
    print(pool_out)
    print('...Pool+Linear layer  is done\n')
    print('Calculating activation layer 2 (square)...\n')
    act_out_2 = []
    for i in range(0, len(pool_out)):
        c_tpm = pool_out[i] * pool_out[i]
        act_out_2.append(c_tpm)
    del pool_out[:]
    print(act_out_2)
    print('...Activation layer 2 is done\n')
    print('Calculating FC layer...\n')
    dot_len = 100
    c_fc_len = 100
    fc_out = []
    for i in range(0, p_fc_len, dot_len):
        for j in range(0, c_fc_len, dot_len):
            dots = []
            for x in range(0, dot_len):
                c_tpm = act_out_2[j + x] * p_fc_vec[i + x]
                dots.append(c_tpm)
            fc_out.append(add_many(dots))
    print('...FC layer is done\n')
    s3.upload_obj(video, 'data', 'video.cpy.in')
    print(fc_out)
    return fc_out


def lambda_handler(event, context):
    r = cryptonets()
    for i, o in enumerate(r):
        s3.upload_obj(o, 'data', 'res.' + str(i) + '.out')
    print('cryptonets done')
    return {'statusCode': 200, 'body': [('res.' + str(i) + '.out') for i in
        range(len(r))]}
