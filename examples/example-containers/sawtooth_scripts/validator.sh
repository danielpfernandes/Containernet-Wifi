#!/bin/bash

if [ -z $1 ]; then
    echo "Invalid command, pass one of the following arguments:"
    echo "validator.sh <argument>"
    echo "  Valid arguments: base1, drone1, drone2, drone3, drone4"
    exit 1
fi

IP=""
VALIDATOR=""

case $1 in
base1) IP='10.0.0.1' VALIDATOR='0';;
drone1) IP='10.0.0.249' VALIDATOR='1';;
drone2) IP='10.0.0.250' VALIDATOR='2';;
drone3) IP='10.0.0.251' VALIDATOR='3';;
drone4) IP='10.0.0.252' VALIDATOR='4';;
*) echo "Invalid option";;
esac 

if [ -e /pbft-shared/validators/validator-${VALIDATOR}.priv ]; then
    cp /pbft-shared/validators/validator-0.pub /etc/sawtooth/keys/validator.pub
    cp /pbft-shared/validators/validator-0.priv /etc/sawtooth/keys/validator.priv
fi &&
if [ ! -e /etc/sawtooth/keys/validator.priv ]; then
    sawadm keygen
    mkdir -p /pbft-shared/validators || true
    cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-${VALIDATOR}.pub
    cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-${VALIDATOR}.priv
fi &&
if [ ! -e config-genesis.batch ]; then
    sawset genesis -k /etc/sawtooth/keys/validator.priv -o /tmp/config-genesis.batch
fi &&
if [ $VALIDATOR = '0' ]; then
    while [[ ! -f /pbft-shared/validators/validator-1.pub || \
                ! -f /pbft-shared/validators/validator-2.pub || \
                ! -f /pbft-shared/validators/validator-3.pub || \
                ! -f /pbft-shared/validators/validator-4.pub ]];
    do sleep 1; done
    PBFT_MEMBERS=$(echo \'['"'$(cat /pbft-shared/validators/validator-0.pub)'"','"'$(cat /pbft-shared/validators/validator-1.pub)'"','"'$(cat /pbft-shared/validators/validator-2.pub)'"','"'$(cat /pbft-shared/validators/validator-3.pub)'"','"'$(cat /pbft-shared/validators/validator-4.pub)'"']\')
    if [ ! -e /tmp/config.batch ]; then
        sawset proposal create \
        -k /etc/sawtooth/keys/validator.priv \
        sawtooth.consensus.algorithm.name=pbft \
        sawtooth.consensus.algorithm.version=1.0 \
        sawtooth.consensus.pbft.members="${PBFT_MEMBERS}" \
        -o /tmp/config.batch
    fi &&
    if [ ! -e /var/lib/sawtooth/genesis.batch ]; then
        sawadm genesis /tmp/config-genesis.batch /tmp/config.batch
    fi
fi &&
if [ ! -e /root/.sawtooth/keys/root.priv ]; then
    sawtooth keygen root
fi &&
sawtooth-validator -vv \
    --endpoint tcp://"${IP}":8800 \
    --bind network:tcp://"${IP}":8800\
    --peers tcp://10.0.0.1:8800,\
            tcp://10.0.0.249:8800,\
            tcp://10.0.0.250:8800,\
            tcp://10.0.0.251:8800,\
            tcp://10.0.0.252:8800
#    --bind component:tcp://127.0.0.1:4004 \
#    --bind consensus:tcp://127.0.0.1:5050 \
#    --bind network:tcp://127.0.0.1:8800 \
#    --scheduler parallel \
#    --peering static \
#    --maximum-peer-connectivity 10000 \