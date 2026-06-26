FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iproute2 \
    tcpdump \
    iputils-ping

RUN pip3 install pandas matplotlib

WORKDIR /app

RUN mkdir -p /app/logs /app/capturas /app/www

COPY src/ /app/
COPY scripts/ /app/scripts/
COPY www/ /app/www/
COPY hosts.txt /app/hosts.txt
