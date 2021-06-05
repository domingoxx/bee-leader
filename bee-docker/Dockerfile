# FROM ethersphere/bee:0.6.2
FROM python:3.8.10

ADD bee-0.6.2.tar.gz /

RUN mkdir -p /opt/data \
    && pip3 install websockets;

ADD py /opt

WORKDIR /opt
VOLUME /opt/data

EXPOSE 1633 1634 1635

ENTRYPOINT ["python3","-m","py.bee.start_bee"]