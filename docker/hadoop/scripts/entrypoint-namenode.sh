#!/bin/bash

# Format namenode if it doesn't exist
if [ ! -d /hadoop/dfs/name/current ]; then
  echo "Formatting namenode directory..."
  $HADOOP_HOME/bin/hdfs namenode -format -force
fi

# Start namenode
echo "Starting HDFS namenode..."
$HADOOP_HOME/bin/hdfs --daemon start namenode

# Keep container running
echo "Namenode started, tail-ing the logs..."
tail -f $HADOOP_HOME/logs/hadoop-root-namenode-*.log