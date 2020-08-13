# SelecltiveCrypt

## Introduction

This repository only contains the proof-of-concept implementation of the
SelectiveCrypt compiler and simple testing framework.  

The SelectiveCrypt compiler determines appropriate cryptographic primitives for
each data item in a AWS Lambda function code based on data usage patterns.  Then
the compiler transforms the original code to enable encrypted data processing
and generates an analysis report.

Since the SelectiveCrypt framework utilizes AWS Lambda, S3, and IoT services, it
requires complex configuration processes such as IAM configuration and client-side
certificates installation.

Therefore, this repository provides a local testing environment using a Lambda
docker and a wrapper S3 library that can be used as both the local storage
service and the actual S3 service.

In addition, this includes minimum configurations to operate in an actual AWS
environment, so please refer to the description below.

## Getting Started

### Local Test

#### Prerequisites 

1. conda
2. docker

#### Prepare local test environment

Clone the project.
Suppose $SELECTIVECRYPT means where the SelectiveCrypt project resides.

``` bash
git clone https://github.com/corelab-src/selectivecrypt
```

If you already have conda or virtualenv, activate your own environment first.

If you don't have any, we recommend Miniconda3. (Suppose you are testing
SelectiveCrypt on x86 Linux machine)
``` bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Libux-x86_64.sh
source ~/.bashrc
conda list
```
Create and activate conda environment.
``` bash
conda create -n <name> python=3.7
source activate <name>
```
Install PyHeal manually.
``` bash
git clone --recursive https://github.com/Accenture/pyheal.git
cd pyheal
pip install .
```
Install required python packages.
``` bash
cd $SELECTIVECRYPT
pip install -t requiremetns.txt
```
For simulating AWS lambda execution locally, we need a lambda docker image.
Pull lambda docker image.
``` bash
docker pull lambci/lambda:python3.7
```
Since AWS Lambda docker mounts local directory as a working directory (like /tmp
of Amazon Linux container for AWS Lambda), you need to install required python
packages on $SELECTIVECRYPT/playground/opt/python directory. 
``` bash 
cd $SELECTIVECRYPT/playground
pip install numpy -t opt/python
cd /path/to/pyheal/
pip install . -t $SELECTIVECRYPT/playground/opt/python
```

#### Compile

``` bash
make cryptonets-local
```
This will produce cryptonets_local_transformed.py in $SELECTIVECRYPT/playground.

#### Run

- Server-side
``` bash
./playground/stay-run.sh cryptonets_local_transformed lambda_handler
```
This script run lambda docker with given lambda function and handler.
Docker container continues to run and waits for invocation.

- Client-side
``` bash
python client/client.py cryptonets local
```

### AWS Test

#### Participants

We use AWS as the cloud, x86 server and Odroid (AArch64) as proxies and
Raspberry Pi as a client device. The proxy is for cryptographic task offloading
(optional).

* Cloud: AWS
* [Proxy: x86 server | Odroid]
* Client: Raspberry Pi

#### AWS Configuration
Suppose you are configuring in the AWS Management Console.  Of course, you can
configure using AWS CLI, SDK, CloudFormation, SAM, or Terraform.
Easy configuration with Terraform or SAM is now in progress.

##### Client Initialization
You need credentials to access AWS service. In IAM dashboard, create individual
an IAM user rather than root access key. With provided access key ID and access
key, run 'aws configure' on client (and proxy) and set them accordingly.

##### Lambda
1. Lambda > Functions, click 'Create function'.
2. For Function name, enter <your_lambda_name>.
3. Choose 'Python 3.7' as runtime
4. **IMPORTANT** Give proper 'execution role' for your a new lambda.
  * Dropdown 'Choose or create an excution role'
  * Select 'Create a new role with bash Lambda permissions'
5. After creation, click 'Edit basic settings' and set 'memory limit' and
   'timeout' to the maximum. (3008 MB and 15 min, respectively)

Read
https://docs.aws.amazon.com/lambda/latest/dg/getting-started-create-function.html

##### IoT
In order to make your device or proxy cooperate with AWS services, uou need AWS
IoT Python SDK (not v2. we use v1) 
Read
* https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdks.html
* https://aws.amazon.com/premiumsupport/knowledge-center/iot-core-publish-mqtt-messages-python/?nc1=h_ls
* https://github.com/aws/aws-iot-device-sdk-python

To use this SDK, we need an IoT Thing (AWS IoT -> Manage -> Things). 
After creating a thing, attach
IoT policies and download certificate, public key, private key and
root certificate of Amazon (rootCA.crt) to your client device.
In my case, my policy attached to Raspberry Pi is as follows.
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:*",
      "Resource": "*"
    }
  ]
}</code></pre>

Properly set $SELECTIVECRYPT/playground/awsiot.---.config.json
you can find "endpoint" at your Things dashboard. 
* AWS IoT -> Manage -> Things -> (your thing) -> Interact, See HTTPS section
Set key paths for certificates. (rootCA, cert, key)
For generality, We unified the names of device certificate and keys
as cert.pem and privkey.pem.

'pub_topic' is a topic where your client or proxy publishes an MQTT message to
invoke <your_lambda_name>.
'sub_topic' is a topic where your client or proxy subscribes an MQTT message for
waiting results from <your_lambda_name>.

In AWS console,
AWS IoT > Act > Rules, choose 'Create'.
Set <your_lambda_rule_name>, and write down the topic that <your_lambda_name>
subscribes in 'Rule query statement'.

In AWS console,
Lambda > Functions, choose <your_lambda_name>.
On configuration tab, choose '+ Add trigger'.
Choose 'AWS IoT', with 'Custom IoT Rule' and select a rule you just made
(<your_lambda_rule_name>).

Set roles..

##### S3
Make your own bucket. In my case, it is 'selcrypt'.
Read https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html

#### Prepare your lambda and lambda layer
The python packages that <your_lambda_name> depends on should be compressed as
zip and uploaded to the lambda layer.
Read https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html

If you already installed 'pyheal' on $SELECTIVECRYPT/playground/opt/python,
you just need zip 'python' directory.
```bash
cd $SELECTIVECRYPT/playground/opt
zip -r pyheal.zip .
``` 
``` bash
make cryptonets
make zip_cryptonets
```
You will see $SELECTIVECRYPT/build/crtyptonets.zip
Now you manually upload the zipped file on your lambda. (Lambda > Functions >
<your_lambda_name>, In Function code box, click 'actions' dropbox menu and
select 'Upload a .zip file')

#### Troubleshooting

## GLIBC 2.29 not found

build pyheal on lower version of linux.

## When building pyheal, virtual memory exhausted

Your device does not have enough memory to build.
See https://stackoverflow.com/questions/29466663/memory-error-while-using-pip-install-matplotlib

```bash
# create swap file of 512 MB
dd if=/dev/zero of=/swapfile bs=1024 count=524288
# modify permissions
chown root:root /swapfile
chmod 0600 /swapfile
# setup swap area
mkswap /swapfile
# turn swap on
swapon /swapfile
```

## After building pyheal, import ... encounter '
