FROM ubuntu:xenial

# install required packages
RUN apt-get clean
RUN apt-get update \
    && apt-get install -y  git \
    net-tools \
    aptitude \
    build-essential \
    python3-setuptools \
    python3-dev \
    python3-pip \
    software-properties-common \
    ansible \
    curl \
    iptables \
    iputils-ping \
    sudo

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.5 1
# install containernet (using its Ansible playbook)
RUN python3 -m pip install --upgrade "pip < 21.0"
RUN python3 -m pip install ansible
COPY . /containernet
WORKDIR /containernet/ansible
RUN ansible-playbook -i "localhost," -c local --skip-tags "notindocker" install.yml
WORKDIR /containernet
RUN python3 setup.py develop

# Hotfix: https://github.com/pytest-dev/pytest/issues/4770
RUN python3 -m pip install "more-itertools<=5.0.0"

# tell containernet that it runs in a container
ENV CONTAINERNET_NESTED 1

# Important: This entrypoint is required to start the OVS service
ENTRYPOINT ["util/docker/entrypoint.sh"]
CMD ["python3", "examples/containernet_example.py"]

