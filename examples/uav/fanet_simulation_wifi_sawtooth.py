#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

import subprocess
import os
from sys import stdout
import time
from mininet.cli import CLI
from mn_wifi.link import adhoc
from mn_wifi.telemetry import telemetry
from mininet.log import info, setLogLevel
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm


def topology():
    setLogLevel('info')

    net = Containernet()

    info('*** Starting monitors')
    grafana = subprocess.Popen(["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    info('\n*** Adding base station\n')
    bs1 = net.addStation('base1', 
                        ip='10.0.0.1',
                        mac='00:00:00:00:00:00',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/base1/data:/data"])

    info('\n*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1', 
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/drone1/root:/root", "/tmp/drone1/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=5, 
                        cpu_period=50000, 
                        cpu_quota=10000,
                        position='30,60,10')

    # OSD33x Family Processor
    d2 = net.addStation('drone2',
                        ip='10.0.0.250',
                        mac='00:00:00:00:00:02',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/drone2/root:/root", "/tmp/drone2/data:/data"],
                        mem_limit=958182016,
                        cpu_shares=2, 
                        cpu_period=50000, 
                        cpu_quota=10000,
                        position='31,61,10')

    # Holybro PX4 Vision
    d3 = net.addStation('drone3', 
                        ip='10.0.0.251',
                        mac='00:00:00:00:00:03',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll", 
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/drone3/root:/root", "/tmp/drone3/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=5, 
                        cpu_period=50000, 
                        cpu_quota=10000,
                        position='50,50,10')

    # Raspberry Pi4 with 2GB RAM
    d4 = net.addStation('drone4', 
                        ip='10.0.0.252',
                        mac='00:00:00:00:00:04',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/drone4/root:/root", "/tmp/drone4/data:/data"],
                        mem_limit=1900182016,
                        cpu_shares=5, 
                        cpu_period=50000, 
                        cpu_quota=10000,
                        position='60,20,10')

    # Jetson Nano ARM Cortex-A57 3 GB LPDDR4
    d5 = net.addStation('drone5',
                        ip='10.0.0.253',
                        mac='00:00:00:00:00:05',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/drone5/root:/root", "/tmp/drone5/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=10, 
                        cpu_period=50000, 
                        cpu_quota=10000,
                        position='20,60,10')

    net.setPropagationModel(model="logDistance", exp=4.5)

    info("\n*** Configuring wifi nodes\n")

    net.configureWifiNodes()

    net.addLink(bs1, cls=adhoc, intf='base1-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(d1, cls=adhoc, intf='drone1-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(d2, cls=adhoc, intf='drone2-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(d3, cls=adhoc, intf='drone3-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(d4, cls=adhoc, intf='drone4-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(d5, cls=adhoc, intf='drone5-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    net.addLink(bs1, cls=adhoc, intf='base1-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')

    info('\n*** Starting network\n')
    net.build()
    net.start()

    #nodes = net.stations
    #telemetry(nodes=nodes, single=True, data_type='position')

    sta_drone = []
    for n in net.stations:
        sta_drone.append(n.name)
    sta_drone_send = ' '.join(map(str, sta_drone))

    # # set_socket_ip: localhost must be replaced by ip address
    # # of the network interface of your system
    # # The same must be done with socket_client.py
    info('\n*** Starting Socket Server\n')
    net.socketServer(ip='127.0.0.1', port=12345)

    info('\n*** Generating drones and base station sawtooth keypairs\n')
    validator_pub_key = {}
    validator_pub_key["d1"] = generate_keypairs(d1)
    validator_pub_key["d2"] = generate_keypairs(d2)
    validator_pub_key["d3"] = generate_keypairs(d3)
    validator_pub_key["d4"] = generate_keypairs(d4)
    validator_pub_key["d5"] = generate_keypairs(d5)
    validator_pub_key["bs1"] = generate_keypairs(bs1)

    info('\n*** Create the Genesis Block on Base Station\n')
    bs1.cmd("sawset genesis --key $HOME/.sawtooth/keys/base1.priv -o /tmp/config-genesis.batch")

    info('\n*** Create a batch to initialize the consensus settings on the Base Station\n')
    create_batch_settings(bs1, validator_pub_key)

    info('\n*** Combining batches in one genesis bath on Base Station ***\n')
    bs1.cmd('sudo -u sawtooth sawadm genesis /tmp/config-genesis.batch /tmp/config-consensus.batch')

    info('\n*** Starting Sawtooth Validator for the Base Station ***\n')
    start_validator(bs1)
    
    info('\n*** Starting Sawtooth REST API for the Base Station ***\n')
    start_rest_api(bs1)

    info('\n*** Starting Sawtooth Transaction Processors for the Base Station ***\n')
    start_transaction_processors(bs1)

    info('\n*** Starting Sawtooth Consensus Mecanism for the Base Station ***\n')
    start_consensus_mecanism(bs1)

    info('\n*** Start drone terminals\n')
    makeTerm(bs1, cmd="bash")
    makeTerm(d1, cmd="bash")
    makeTerm(d2, cmd="bash")
    makeTerm(d3, cmd="bash")
    makeTerm(d4, cmd="bash")
    makeTerm(d5, cmd="bash")


    # info("*** Starting CoppeliaSim\n")
    path = os.path.dirname(os.path.abspath(__file__))
    # os.system('{}/CoppeliaSim_Edu_V4_1_0_Ubuntu/coppeliaSim.sh -s {}'
    #             '/simulation.ttt -gGUIITEMS_2 &'.format(path, path))
    # time.sleep(10)

    info("\n*** Perform a simple test\n")
    simpleTest = 'python {}/simpleTest.py '.format(path) + sta_drone_send + ' &'
    os.system(simpleTest)

    time.sleep(5)

    info("\n*** Configure the node position\n")
    #setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    #os.system(setNodePosition)

    info('\n*** Running CLI\n')
    CLI(net)

    info('\n*** Stopping network')
    kill_process()
    net.stop()
    grafana.kill()

def set_location(station, iterations=10, interval=10, target ='10.0.0.249', coordinates='0 0 0'):
    for number in range(iterations):
        station.cmd('python /rest/setLocation.py ' 
                    + target + ' ' 
                    + coordinates + ' True &')
        time.sleep(interval)
        print("Iteration number " + str(number + 1) + " of " + str(iterations))

def start_validator(node):
    ip = str(node.params.get('ip'))
    peers = ["10.0.0.1", "10.0.0.249", "10.0.0.250", "10.0.0.251", "10.0.0.252", "10.0.0.253"]
    peers.remove(ip)
    makeTerm(node=node, title=str(node.name) + ' Validator', cmd='sudo -u sawtooth sawtooth-validator \
        --bind component:tcp://127.0.0.1:4004 \
        --bind network:tcp://' + ip + ':8800 \
        --bind consensus:tcp://' + ip + ':5050 \
        --endpoint tcp://' + ip + ':8800 \
        --peers tcp://' + peers[0] 
        + ':8800, tcp://' + peers[1] 
        + ':8800, tcp://' + peers[2] 
        + ':8800, tcp://' + peers[3] 
        + ':8800, tcp://' + peers[4] + ':8800')

def start_rest_api(node):
    makeTerm(node=node, title=str(node.name) + ' REST API', cmd='sudo -u sawtooth sawtooth-rest-api -v')

def start_transaction_processors(node):
    makeTerm(node=node,title=str(node.name) + ' Transaction Settings', cmd='sudo -u sawtooth settings-tp -v')
    makeTerm(node=node, title=str(node.name) + ' Intkey Processor', cmd='sudo -u sawtooth intkey-tp-python -v')

def start_consensus_mecanism(node):
    makeTerm(node=node, title=str(node.name) + ' Consensus Mecanism', cmd='sudo -u sawtooth pbft-engine -vv --connect tcp://localhost:5050')

def generate_keypairs(node):
    node.cmd("sawtooth keygen " + str(node.name))
    node.cmd("sawadm keygen")
    return node.cmd("cat /etc/sawtooth/keys/validator.pub")

def create_batch_settings(node, validator_pub_key_dict):
    node.cmd("sawset proposal create --key $HOME/.sawtooth/keys/" + str(node.name) + ".priv \
    -o /tmp/config-consensus.batch \
    sawtooth.consensus.algorithm.name=pbft \
    sawtooth.consensus.algorithm.version=1.0 \
    sawtooth.consensus.pbft.members='[\"" 
    + str(validator_pub_key_dict["d1"])+ "\",\""
    + str(validator_pub_key_dict["d2"])+ "\",\""
    + str(validator_pub_key_dict["d3"])+ "\",\""
    + str(validator_pub_key_dict["d4"])+ "\",\""
    + str(validator_pub_key_dict["d5"])+ "\",\""
    + str(validator_pub_key_dict["bs1"])+ "\"]'")


def kill_process():
    #os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    topology()
