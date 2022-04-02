#!/bin/bash

if [ -z "$1" ]; then
    echo "Invalid command, pass one of the following arguments:"
    echo "validator.sh <argument>"
    echo "  Valid arguments: base1, drone1, drone2, drone3, drone4"
    exit 1
fi

rm -rf /var/lib/sawtooth/*
rm -rf /var/log/sawtooth/*

IP=""
VALIDATOR=""
PEERS=""
BASE1_IP='10.0.0.1'
DRONE1_IP='10.0.0.249'
DRONE2_IP='10.0.0.250'
DRONE3_IP='10.0.0.251'
DRONE4_IP='10.0.0.252'
VALIDATOR_PRIV="/etc/sawtooth/keys/validator.priv"
VALIDATOR_PUB="/etc/sawtooth/keys/validator.pub"

case $1 in
base1)  IP=$BASE1_IP  VALIDATOR='0' PEERS="tcp://${DRONE1_IP}:8800,tcp://${DRONE2_IP}:8800,tcp://${DRONE3_IP},tcp://${DRONE4_IP}:8800";;
drone1) IP=$DRONE1_IP VALIDATOR='1' PEERS="tcp://${BASE1_IP}:8800,tcp://${DRONE2_IP}:8800,tcp://${DRONE3_IP},tcp://${DRONE4_IP}:8800";;
drone2) IP=$DRONE2_IP VALIDATOR='2' PEERS="tcp://${BASE1_IP}:8800,tcp://${DRONE1_IP}:8800,tcp://${DRONE3_IP},tcp://${DRONE4_IP}:8800";;
drone3) IP=$DRONE3_IP VALIDATOR='3' PEERS="tcp://${BASE1_IP}:8800,tcp://${DRONE1_IP}:8800,tcp://${DRONE2_IP},tcp://${DRONE4_IP}:8800";;
drone4) IP=$DRONE4_IP VALIDATOR='4' PEERS="tcp://${BASE1_IP}:8800,tcp://${DRONE1_IP}:8800,tcp://${DRONE2_IP},tcp://${DRONE3_IP}:8800";;
*) echo "Invalid option";;
esac 

if [ -e /poet-shared/validators/validator-${VALIDATOR}.priv ]; then
    cp /poet-shared/validators/validator-${VALIDATOR}.pub $VALIDATOR_PUB
    cp /poet-shared/validators/validator-${VALIDATOR}.priv $VALIDATOR_PRIV
fi &&
if [ ! -e $VALIDATOR_PRIV ]; then
    sawadm keygen
    mkdir -p /poet-shared/validators || true
    cp $VALIDATOR_PUB /poet-shared/validators/validator-${VALIDATOR}.pub
    cp $VALIDATOR_PRIV /poet-shared/validators/validator-${VALIDATOR}.priv
fi &&
if [ ! -e config-genesis.batch ]; then
    sawset genesis -k $VALIDATOR_PRIV -o /tmp/config-genesis.batch
fi &&
if [ $VALIDATOR = '0' ]; then
    ## FOR PBFT:
    # while [[ ! -f /pbft-shared/validators/validator-1.pub || \
    #             ! -f /pbft-shared/validators/validator-2.pub || \
    #             ! -f /pbft-shared/validators/validator-3.pub || \
    #             ! -f /pbft-shared/validators/validator-4.pub ]];
    # do sleep 1; done
    # PBFT_MEMBERS=$(echo ['"'$(cat /pbft-shared/validators/validator-0.pub)'"','"'$(cat /pbft-shared/validators/validator-1.pub)'"','"'$(cat /pbft-shared/validators/validator-2.pub)'"','"'$(cat /pbft-shared/validators/validator-3.pub)'"','"'$(cat /pbft-shared/validators/validator-4.pub)'"'])
    if [ ! -e /tmp/config-consensus.batch ]; then
        sawset proposal create --key $VALIDATOR_PRIV \
            -o /tmp/config-consensus.batch \
            sawtooth.consensus.algorithm.name=PoET \
            sawtooth.consensus.algorithm.version=0.1 \
            sawtooth.poet.report_public_key_pem="$(cat /etc/sawtooth/simulator_rk_pub.pem)" \
            sawtooth.poet.valid_enclave_measurements=$(poet enclave measurement) \
            sawtooth.poet.valid_enclave_basenames=$(poet enclave basename)
        
        sawset proposal create --key $VALIDATOR_PRIV \
            -o /tmp/poet-settings.batch \
            sawtooth.poet.target_wait_time=5 \
            sawtooth.poet.initial_wait_time=25 \
            sawtooth.publisher.max_batches_per_block=100

        # For PBFT:
        # sawset proposal create \
        # -k $VALIDATOR_PRIV \
        # sawtooth.consensus.algorithm.name=pbft \
        # sawtooth.consensus.algorithm.version=1.0 \
        # sawtooth.consensus.pbft.members="${PBFT_MEMBERS}" \
        # -o /tmp/config-consensus.batch

        poet registration create --key $VALIDATOR_PRIV -o /tmp/poet.batch

    fi &&
    if [ ! -e /var/lib/sawtooth/genesis.batch ]; then
        # For PBFT:    
        # sawadm genesis /tmp/config-genesis.batch /tmp/config-consensus.batch
        sudo -u sawtooth sawadm genesis /tmp/config-genesis.batch /tmp/config-consensus.batch /tmp/poet.batch /tmp/poet-settings.batch
    fi
fi &&
if [ ! -e /root/.sawtooth/keys/root.priv ]; then
    sawtooth keygen root
fi &&
sawtooth-validator -vv \
    --endpoint tcp://${IP}:8800 \
    --bind network:tcp://${IP}:8800 \
    --bind component:tcp://${IP}:4004 \
    --peers $PEERS

##### Other options
#    --bind component:tcp://127.0.0.1:4004 \
#    --bind consensus:tcp://127.0.0.1:5050 \
#    --bind network:tcp://127.0.0.1:8800 \
#    --scheduler parallel \
#    --peering static \
#    --maximum-peer-connectivity 10000 \
