FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    curl \
    net-tools \
    netcat-openbsd \
    gnupg \
    procps \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV ZOOKEEPER_HOME=/opt/zookeeper
ENV ZOOKEEPER_VERSION=3.8.4
ENV PATH=${PATH}:${ZOOKEEPER_HOME}/bin

# Copy Zookeeper distribution
COPY packages/apache-zookeeper-3.8.4-bin.tar.gz /tmp/
RUN tar -xzf /tmp/apache-zookeeper-3.8.4-bin.tar.gz -C /opt/ && \
    ln -s /opt/apache-zookeeper-${ZOOKEEPER_VERSION}-bin ${ZOOKEEPER_HOME} && \
    rm /tmp/apache-zookeeper-3.8.4-bin.tar.gz

# Create data and log directories
RUN mkdir -p /data /datalog

# Copy configuration
COPY docker/zookeeper/config/zoo.cfg ${ZOOKEEPER_HOME}/conf/

# Set up entrypoint script
COPY docker/zookeeper/scripts/entrypoint-zookeeper.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 2181 2888 3888

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]