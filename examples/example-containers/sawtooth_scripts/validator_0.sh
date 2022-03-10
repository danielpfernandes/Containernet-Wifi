#!/bin/bash

if [ -e /pbft-shared/validators/validator-0.priv ]; then
    cp /pbft-shared/validators/validator-0.pub /etc/sawtooth/keys/validator.pub
    cp /pbft-shared/validators/validator-0.priv /etc/sawtooth/keys/validator.priv
fi &&
if [ ! -e /etc/sawtooth/keys/validator.priv ]; then
    sawadm keygen
    mkdir -p /pbft-shared/validators || true
    cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-0.pub
    cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-0.priv
fi &&
if [ ! -e config-genesis.batch ]; then
    sawset genesis -k /etc/sawtooth/keys/validator.priv -o config-genesis.batch
fi &&
while [[ ! -f /pbft-shared/validators/validator-1.pub || \
            ! -f /pbft-shared/validators/validator-2.pub || \
            ! -f /pbft-shared/validators/validator-3.pub || \
            ! -f /pbft-shared/validators/validator-4.pub ]];
do sleep 1; done
echo 'sawtooth.consensus.pbft.members=\\['\"'$$(cat /pbft-shared/validators/validator-0.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-1.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-2.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-3.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-4.pub)'\"'\\] &&'
if [ ! -e config.batch ]; then
    bash -c 'sawset proposal create \
    -k /etc/sawtooth/keys/validator.priv \
    sawtooth.consensus.algorithm.name=pbft \
    sawtooth.consensus.algorithm.version=1.0 \
    sawtooth.consensus.pbft.members=\\['\"'$$(cat /pbft-shared/validators/validator-0.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-1.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-2.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-3.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-4.pub)'\"'\\] \
    sawtooth.publisher.max_batches_per_block=1200 \
    -o config.batch'
fi &&
if [ ! -e /var/lib/sawtooth/genesis.batch ]; then
    sawadm genesis config-genesis.batch config.batch
fi &&
if [ ! -e /root/.sawtooth/keys/root.priv ]; then
    sawtooth keygen root
fi &&
sawtooth-validator -vv \
    --endpoint tcp://10.0.0.1:8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --bind consensus:tcp://eth0:5050 \
    --bind network:tcp://10.0.0.1:8800 \
    --scheduler parallel \
    --peering static \
    --maximum-peer-connectivity 10000 \
    --peers tcp://10.0.0.1:8800, \
            tcp://10.0.0.249:8800, \
            tcp://10.0.0.250:8800, \
            tcp://10.0.0.251:8800, \
            tcp://10.0.0.252:8800