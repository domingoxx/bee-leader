FROM ethersphere/bee:0.5.3

USER root

ADD start_bee.sh /opt
RUN chmod 755 /opt/start_bee.sh && mkdir -p /opt/bee

VOLUME /opt/bee

ENTRYPOINT ["/opt/start_bee.sh"]