FROM continuumio/miniconda3

WORKDIR /root

RUN apt -y -qq update && apt -y -qq upgrade
RUN apt -y -qq install \
    build-essential \
    curl \
    wget \
    git \
    vim \
    gcc \
    g++ && \
    rm -rf /var/lib/apt/lists/*

RUN pip install numpy 
RUN pip install gast, beniget
RUN pip install pycrypto
RUN pip install pyaes
