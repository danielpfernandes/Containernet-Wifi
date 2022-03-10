#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

import subprocess
import os
import time
from sys import stdout
from mininet.cli import CLI
from mn_wifi.link import adhoc
from mn_wifi.telemetry import telemetry
from mininet.log import info, setLogLevel
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm
from fanet_utils import create_batch_settings, generate_keypairs, initialize_sawtooth, kill_process


def topology():
    setLogLevel('info')
    PORTS = [4004, 8008, 8800, 5050, 3030, 5000]
    DOCKER_IMAGE = "containernet_example:sawtoothAll"

    net = Containernet()

    info('*** Starting monitors')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    info('\n*** Adding base station\n')

    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage=DOCKER_IMAGE,
                         ports=PORTS,
                         volumes=["/tmp/base1/data:/data",
                                  "/tmp/pbft-shared:/pbft-shared"])

    info('\n*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage=DOCKER_IMAGE,
                        ports=PORTS,
                        volumes=["/tmp/drone1/root:/root",
                                 "/tmp/drone1/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
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
                        dimage=DOCKER_IMAGE,
                        ports=PORTS,
                        volumes=["/tmp/drone2/root:/root",
                                 "/tmp/drone2/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
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
                        dimage=DOCKER_IMAGE,
                        ports=PORTS,
                        volumes=["/tmp/drone3/root:/root",
                                 "/tmp/drone3/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
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
                        dimage=DOCKER_IMAGE,
                        ports=PORTS,
                        volumes=["/tmp/drone4/root:/root",
                                 "/tmp/drone4/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
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
                        dimage=DOCKER_IMAGE,
                        ports=PORTS,
                        volumes=["/tmp/drone5/root:/root",
                                 "/tmp/drone5/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
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

    # info('\n*** Generating drones and base station sawtooth keypairs\n')
    # validator_pub_key = {}
    # validator_pub_key["d1"] = generate_keypairs(d1)
    # validator_pub_key["d2"] = generate_keypairs(d2)
    # validator_pub_key["d3"] = generate_keypairs(d3)
    # validator_pub_key["d4"] = generate_keypairs(d4)
    # validator_pub_key["d5"] = generate_keypairs(d5)
    # validator_pub_key["bs1"] = generate_keypairs(bs1)

    # info('\n*** Create the Genesis Block on Base Station\n')
    # bs1.cmd(
    #     "sawset genesis --key $HOME/.sawtooth/keys/root.priv -o /tmp/config-genesis.batch")

    # info('\n*** Create a batch to initialize the consensus settings on the Base Station\n')
    # create_batch_settings(bs1, validator_pub_key)

    # info('\n*** Combining batches in one genesis bath on Base Station ***\n')
    # bs1.cmd('sudo -u sawtooth sawadm genesis /tmp/config-genesis.batch /tmp/config-consensus.batch')

    info('\n*** Starting Sawtooth on the Base Station ***\n')
    initialize_sawtooth(bs1, should_open_terminal=True)

    info('\n*** Starting Sawtooth on the Drones ***\n')
    initialize_sawtooth(d1, should_open_terminal=True)
    initialize_sawtooth(d2, should_open_terminal=True)
    initialize_sawtooth(d3)
    initialize_sawtooth(d4)
    #initialize_sawtooth(d5)

    # info('\n*** Start drone terminals\n')
    makeTerm(bs1, cmd="bash")
    makeTerm(d1, cmd="bash")
    # makeTerm(d2, cmd="bash")
    # makeTerm(d3, cmd="bash")
    # makeTerm(d4, cmd="bash")
    # makeTerm(d5, cmd="bash")

    # info("*** Starting CoppeliaSim\n")
    path = os.path.dirname(os.path.abspath(__file__))
    # os.system('{}/CoppeliaSim_Edu_V4_1_0_Ubuntu/coppeliaSim.sh -s {}'
    #             '/simulation.ttt -gGUIITEMS_2 &'.format(path, path))
    # time.sleep(10)

    info("\n*** Perform a simple test\n")
    simpleTest = 'python {}/simpleTest.py '.format(
        path) + sta_drone_send + ' &'
    os.system(simpleTest)

    time.sleep(5)

    info("\n*** Configure the node position\n")
    #setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    info('\n*** Running CLI\n')
    CLI(net)

    info('\n*** Stopping network')
    kill_process()
    net.stop()
    grafana.kill()


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    topology()
