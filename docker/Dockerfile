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
    g++ \
    cmake && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -t requirements.txt
RUN git clone --recursive https://github.com/Accenture/pyheal.git
RUN cd pyheal && pip install .
