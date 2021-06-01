# FROM ethersphere/bee:0.6.2
FROM python:3.8.10

USER root

ADD clef.tar.gz /
ADD bee.tar.gz /
ADD start_bee.py /
RUN mkdir -p /opt/bee \
    && pip3 install websockets;
    # && apt-get update \
    # && apt-get install -y curl netcat \
    # && apt-get clean \
    # && rm -rf /var/lib/apt/lists/*;
    
WORKDIR /opt/bee
VOLUME /opt/data

EXPOSE 1633 1634 1635

ENTRYPOINT ["python3","/start_bee.py"]