#!/bin/bash

if [ -e /pbft-shared/validators/validator-2.priv ]; then
    cp /pbft-shared/validators/validator-2.pub /etc/sawtooth/keys/validator.pub
    cp /pbft-shared/validators/validator-2.priv /etc/sawtooth/keys/validator.priv
fi &&
if [ ! -e /etc/sawtooth/keys/validator.priv ]; then
    sawadm keygen
    mkdir -p /pbft-shared/validators || true
    cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-2.pub
    cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-2.priv
fi &&
if [ ! -e /root/.sawtooth/keys/root.priv ]; then
    sawtooth keygen root
fi &&
sawtooth-validator -vv \
    --endpoint tcp://10.0.0.250:8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --bind consensus:tcp://eth0:5050 \
    --bind network:tcp://10.0.0.250:8800 \
    --scheduler parallel \
    --peering static \
    --maximum-peer-connectivity 10000 \
    --peers tcp://10.0.0.1:8800, \
            tcp://10.0.0.249:8800, \
            tcp://10.0.0.250:8800, \
            tcp://10.0.0.251:8800, \
            tcp://10.0.0.252:8800