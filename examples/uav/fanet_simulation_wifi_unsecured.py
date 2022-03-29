#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

import os
import subprocess
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mn_wifi.link import adhoc

from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm
from examples.uav.fanet_utils import set_location, setup_network


def topology():
    setLogLevel('info')

    net = Containernet()

    info('*** Starting monitors')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)

    info('\n*** Adding base station\n')
    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage="containernet_example:sawtoothAll",
                         ports=[4004, 8008, 8800, 5050, 3030, 5000],
                         volumes=["/tmp/base1/data:/data"])

    info('\n*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone1/root:/root",
                                 "/tmp/drone1/data:/data"],
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
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone2/root:/root",
                                 "/tmp/drone2/data:/data"],
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
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone3/root:/root",
                                 "/tmp/drone3/data:/data"],
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
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone4/root:/root",
                                 "/tmp/drone4/data:/data"],
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
                        ports=[4004, 8008, 8800, 5050, 3030, 5000],
                        volumes=["/tmp/drone5/root:/root",
                                 "/tmp/drone5/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=10,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='20,60,10')

    setup_network(net, bs1, d1, d2, d3, d4, d5)

    info('\n*** Starting REST server on drones\n')
    d1.cmd('touch /data/locations.csv && python /rest/locationRestServer.py &')
    d2.cmd('touch /data/locations.csv && python /rest/locationRestServer.py &')
    d3.cmd('touch /data/locations.csv && python /rest/locationRestServer.py &')
    d4.cmd('touch /data/locations.csv && python /rest/locationRestServer.py &')
    d5.cmd('touch /data/locations.csv && python /rest/locationRestServer.py &')

    info('\n*** Starting Validation REST server on base station\n')
    bs1.cmd('python /rest/locationRestServer.py &')

    info('\n*** Start drone terminals\n')
    makeTerm(bs1, cmd="bash")
    makeTerm(d1, cmd="tail -f /data/locations.csv")
    makeTerm(d2, cmd="tail -f /data/locations.csv")
    makeTerm(d3, cmd="tail -f /data/locations.csv")
    makeTerm(d4, cmd="tail -f /data/locations.csv")
    makeTerm(d5, cmd="tail -f /data/locations.csv")

    time.sleep(5)

    info("\n*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)

    info("\n*** Scenario 1: BS1 sends initial coordinates to Drone 5\n")
    set_location(bs1, iterations=30, interval=5,
                 target='10.0.0.253', coordinates='11 11 11')

    info("\n*** Scenario 2: BS1 changes the destination coordinates through Drone 2\n")
    set_location(bs1, iterations=30, interval=5,
                 target='10.0.0.250', coordinates='22 22 22')

    info("\n*** Scenario 3: Drone 4 is compromised and  tries to change the destination coordinates\n")
    set_location(d4, iterations=30, interval=5,
                 target='10.0.0.249', coordinates='33 33 33')

    info("\n*** Scenario 4: Connection with the base station is lost and \
the compromised drone tries to change the destination coordinates\n")
    bs1.cmd("pkill -9 -f /rest/locationRestServer.py &")
    set_location(d4, iterations=30, interval=5,
                 target='10.0.0.250', coordinates='44 44 44')

    info("\n*** Scenario 5: A compromised base station joins the network tries to change the destination coordinates\n")
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
    set_location(bs2, iterations=30, interval=5,
                 target='10.0.0.251', coordinates='55 55 55')

    info('\n*** Running CLI\n')
    CLI(net)

    info('\n*** Stopping network')
    kill_process()
    net.stop()
    grafana.kill()


def kill_process():
    # os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    topology()
