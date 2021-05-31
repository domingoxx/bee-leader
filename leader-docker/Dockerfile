FROM python:3.8.10

ADD bee-leader.py /
RUN mkdir -p /opt/data/db && pip3 install flask
WORKDIR /opt/data
VOLUME /opt/data

CMD ["python3", "/bee-leader.py"]