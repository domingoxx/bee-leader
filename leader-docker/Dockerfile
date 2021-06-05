FROM python:3.8.10

RUN mkdir -p /opt/db && pip3 install flask==1.1.4 flask_sockets

ADD py /opt/py

WORKDIR /opt
VOLUME /opt/db
EXPOSE 3000

CMD ["python3", "-m", "py.leader.start_leader"]