#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

import os
import time
from mininet.cli import CLI
from mn_wifi.link import adhoc
from mn_wifi.telemetry import telemetry
from mininet.log import info, setLogLevel
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm, makeTerms

def topology():
    setLogLevel('info')

    net = Containernet()

    info('*** Adding base station\n')
    bs1 = net.addStation('base1', 
                        ip='10.0.0.1',
                        mac='00:00:00:00:00:00',
                        cls=DockerSta,
                        dimage="containernet_example:sawtoothAll",
                        ports=[4004,8008,8800,5050,3030,5000],
                        volumes=["/tmp/base1:/root"])

    info('*** Adding docker drones\n')

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

    info("*** Configuring wifi nodes\n")
    ap1 = net.addAccessPoint('ap1')
    c0 = net.addController('c0')
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

    info('*** Starting network\n')
    net.build()
    net.start()
    # ap1.start([c0])

    #nodes = net.stations
    #telemetry(nodes=nodes, single=True, data_type='position')

    sta_drone = []
    for n in net.stations:
        sta_drone.append(n.name)
    sta_drone_send = ' '.join(map(str, sta_drone))

    # # set_socket_ip: localhost must be replaced by ip address
    # # of the network interface of your system
    # # The same must be done with socket_client.py
    info("*** Starting Socket Server\n")
    net.socketServer(ip='127.0.0.1', port=12345)

    info('*** Starting REST server on drones\n')
    d1.cmd('python /rest/locationRestServer.py &')
    d2.cmd('python /rest/locationRestServer.py &')
    d3.cmd('python /rest/locationRestServer.py &')
    d4.cmd('python /rest/locationRestServer.py &')
    d5.cmd('python /rest/locationRestServer.py &')

    info('*** Start drone terminals')
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

    info("*** Perform a simple test\n")
    simpleTest = 'python {}/simpleTest.py '.format(path) + sta_drone_send + ' &'
    os.system(simpleTest)

    time.sleep(5)

    info("*** Configure the node position\n")
    #setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    #os.system(setNodePosition)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    kill_process()
    net.stop()

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
