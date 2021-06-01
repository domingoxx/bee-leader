FROM python:3.8.10

ADD bee-leader.py /
RUN mkdir -p /opt/data/db && pip3 install flask flask_sockets
WORKDIR /opt/data
VOLUME /opt/data/db
EXPOSE 3000

CMD ["python3", "/bee-leader.py"]