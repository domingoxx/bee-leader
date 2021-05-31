FROM ethersphere/bee:0.5.3

USER root

ADD start_bee.sh /
ADD wait_for.sh /
RUN chmod 755 /opt/start_bee.sh \
    && mkdir -p /opt/bee \
    && apt-get update \
    && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;
    
WORKDIR /opt/bee
VOLUME /opt/bee

ENTRYPOINT ["/start_bee.sh"]