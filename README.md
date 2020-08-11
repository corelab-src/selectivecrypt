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

If you don't have any, I recommend Miniconda3. (Suppose you are testing
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
For simulating AWS lambda execution locally, we provide a script that
run a lambda on lambda docker container.

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
python compile.py lambda.py
```
This will produce 

#### Run

Server-side
``` bash
./stay-run.sh
```

Client-side
``` bash
python client.sh
```
### AWS Test


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
