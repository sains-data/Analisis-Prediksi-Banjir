#!/bin/bash

# Wait for namenode to be available
echo "Waiting for namenode..."
until nc -z namenode 9870; do
  sleep 2
done
echo "Namenode is up"

# Start datanode
echo "Starting HDFS datanode..."
$HADOOP_HOME/bin/hdfs --daemon start datanode

# Keep container running
echo "Datanode started, tail-ing the logs..."
tail -f $HADOOP_HOME/logs/hadoop-root-datanode-*.log