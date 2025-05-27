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
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_VERSION=3.4.1
ENV HIVE_HOME=/opt/hive
ENV HIVE_VERSION=4.0.1
ENV DERBY_HOME=/opt/derby
ENV DERBY_VERSION=10.14.2.0
ENV PATH=${PATH}:${HADOOP_HOME}/bin:${HIVE_HOME}/bin:${DERBY_HOME}/bin

# Copy Hadoop distribution
COPY packages/hadoop-3.4.1.tar.gz /tmp/
RUN tar -xzf /tmp/hadoop-3.4.1.tar.gz -C /opt/ && \
    ln -s /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm /tmp/hadoop-3.4.1.tar.gz

# Copy Hive distribution
COPY ./packages/apache-hive-4.0.1-bin.tar.gz /tmp/
RUN tar -xzf /tmp/apache-hive-4.0.1-bin.tar.gz -C /opt/ && \
    ln -s /opt/apache-hive-${HIVE_VERSION}-bin ${HIVE_HOME} && \
    rm /tmp/apache-hive-4.0.1-bin.tar.gz

# Copy Derby distribution
COPY ./packages/db-derby-10.14.2.0-bin.tar.gz /tmp/
RUN tar -xzf /tmp/db-derby-10.14.2.0-bin.tar.gz -C /opt/ && \
    ln -s /opt/db-derby-${DERBY_VERSION}-bin ${DERBY_HOME} && \
    rm /tmp/db-derby-10.14.2.0-bin.tar.gz

# Create directories for Derby metastore
RUN mkdir -p /opt/derby-metastore

# Set up Hive configuration
COPY docker/hive/config/hive-site.xml ${HIVE_HOME}/conf/
COPY docker/hive/config/hive-env.sh ${HIVE_HOME}/conf/

# Set up entrypoint script
COPY docker/hive/scripts/entrypoint-hive.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 10000 10002 9083

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]