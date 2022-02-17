sudo docker run -d --name=cadvisor -p 8080:8080 --volume=/var/run:/var/run:rw --volume=/sys:/sys:ro --volume=/var/lib/docker/:/var/lib/docker:ro google/cadvisor:latest
sudo docker run -d --name=grafana  -p 3000:3000 --volume=grafana-storage:/var/lib/grafana:rw grafana/grafana:latest
./prometheus/prometheus --config.file=prometheus/prometheus.yml