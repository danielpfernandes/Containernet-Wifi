#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

import os
import subprocess
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel

from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm
from mn_wifi.link import adhoc
from fanet_utils import get_sawtooth_destination, initialize_sawtooth, kill_process, set_sawtooth_destination, set_rest_location, setup_network


def topology():
    setLogLevel('info')
    ports = [4004, 8008, 8800, 5050, 3030, 5000]
    docker_image = "containernet_example:sawtoothAll"

    net = Containernet()

    info('*** Starting monitors')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    info('\n*** Adding base station\n')

    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage=docker_image,
                         ports=ports,
                         port_bindings={88: 8008, 8008: 88},
                         volumes=["/tmp/base1/data:/data",
                                  "/tmp/pbft-shared:/pbft-shared"])

    info('\n*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage=docker_image,
                        ports=ports,
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
                        dimage=docker_image,
                        ports=ports,
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
                        dimage=docker_image,
                        ports=ports,
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
                        dimage=docker_image,
                        ports=ports,
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
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone5/root:/root",
                                 "/tmp/drone5/data:/data",
                                 "/tmp/pbft-shared:/pbft-shared"],
                        mem_limit=3900182016,
                        cpu_shares=10,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='20,60,10')

    setup_network(net, bs1, d1, d2, d3, d4, d5)

    info('\n*** Starting Sawtooth on the Base Station ***\n')
    initialize_sawtooth(bs1, should_open_terminal=True, wait_time_in_seconds=5)

    info('\n*** Starting Sawtooth on the Drones ***\n')
    initialize_sawtooth(d1, wait_time_in_seconds=5)
    initialize_sawtooth(d2, wait_time_in_seconds=5)
    initialize_sawtooth(d3, wait_time_in_seconds=5)
    initialize_sawtooth(d4, wait_time_in_seconds=5)

    time.sleep(10)

    # info("\n*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    info(
        "\n*** Scenario 6: BS1 sends the new coordinates and the Sawtooth network validates the update of the information\n")
    set_sawtooth_destination(bs1, 66, 66, 66)

    info(
        "\n*** Scenario 7: Drone 3 need to rearrange the coordinates and the Sawtooth network validates the update of the information\n")
    set_sawtooth_destination(d3, 77, 77, 77)

    info("\n*** Scenario 8: A compromised Drone in the FANET tries to send a false destination update command to the other UAVs using the unprotected REST Interface, without the possibility to validate the information with the BS1\n")
    set_rest_location(d4, iterations=5, interval=5,
                 target='10.0.0.249', coordinates='88 88 88')
    
    info("\n*** Scenario 9: The connection with BS1 is lost and Drone 2 has to rearrange its coordinates")
    bs1.terminate()
    set_sawtooth_destination(d2, 99, 99, 99)

    info("\n*** Scenario10: A compromised base station joins the network tries to change the destination coordinates\n")
    bs2 = net.addStation('base2',
                         ip='10.0.0.101',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage="containernet_example:sawtoothAll",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base2:/root"])
    net.addLink(bs2, cls=adhoc, intf='base2-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')
    makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations=5, interval=5,
                 target='10.0.0.250', coordinates='10 10 10')
                 
    time.sleep(5)

    info(get_sawtooth_destination(d1))

    info('\n*** Start drone terminals\n')
    makeTerm(bs1, cmd="bash")
    makeTerm(d1, cmd="bash")
    makeTerm(d2, cmd="bash")
    makeTerm(d3, cmd="bash")
    makeTerm(d4, cmd="bash")

    info('\n*** Running CLI\n')
    CLI(net)

    info('\n*** Stopping network\n')
    kill_process()
    net.stop()
    grafana.kill()


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    topology()
