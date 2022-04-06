#!/bin/bash
sudo docker run -d --name=cadvisor -p 8080:8080 --volume=/var/run:/var/run:rw --volume=/sys:/sys:ro --volume=/var/lib/docker/:/var/lib/docker:ro google/cadvisor:latest
sudo docker run -d --name=grafana  -p 3000:3000 --volume=grafana-storage:/var/lib/grafana:rw grafana/grafana:latest
PROMETHEUS="prometheus/prometheus"
if [ ! -f "$PROMETHEUS" ]; then
    curl -LJO https://github.com/prometheus/prometheus/releases/download/v2.34.0/prometheus-2.34.0.linux-amd64.tar.gz && tar -xzf prometheus-2.34.0.linux-amd64.tar.gz && mv prometheus-2.34.0.linux-amd64 prometheus && rm -rf prometheus-2.34.0.linux-amd64.tar.gz
fi
rm -rf prometheus-2.34.0.linux-amd64.tar.gz
./prometheus/prometheus --config.file=prometheus.yml