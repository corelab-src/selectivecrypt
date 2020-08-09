# SelCrypt

## Introduction

The SelCrypt compiler determines an appropriate cryptographic
primitive for each data item in a function code, and transforms the
original code to enable encrypted data processing.

This repository only contains SelCrypt compiler, not the runtime.
Here, you can check how the compiler transforms an original function
code (lambda) to HE-enabled function code (lambda). After compilation,
you will see transformed function code and analysis report. Analysis
report contains which data should be encrypted 

## Getting Started

#### Prerequisites 

1. python
2. conda
3. docker

#### Prerequisites (Python Packages)

1. pycrypto
2. pyaes
3. pyheal
  * git clone --recursive https://github.com/Accenture/pyheal.git
  * cd pyheal
  * pip install .
4. AWSIoTPythonSDK
5. awscli

#### Prepare local test environment

``` bash
cd /path/to/selcryptc/playground
pip install numpy -t opt/python
```

For simulating AWS lambda execution locally, we provide a script that
run a lambda on lambda docker container.

Pull lambda docker image.
``` bash
docker pull lambci/lambda:python3.7
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
