FROM ubuntu:20.04

ENV PYTHONUNBUFFERED 1

RUN set -ex \
	&& apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
        python3-pip \
	&& rm -rf /var/lib/apt/lists/*

RUN wget -O- https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.8/EasyRSA-3.0.8.tgz \
    | tar -C / -zx \
    && mv /EasyRSA-3.0.8 /easy-rsa

WORKDIR /usr/src/project

# install dependencies
COPY ./requirements.txt /usr/src/project/
RUN pip install -r requirements.txt 

# copy project
COPY . /usr/src/project/
