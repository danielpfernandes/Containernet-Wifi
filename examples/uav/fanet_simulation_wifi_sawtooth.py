#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""

from multiprocessing.connection import wait
import os
import subprocess
import sys
import time

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mn_wifi.link import adhoc
from containernet.net import Containernet
from containernet.node import DockerSta
from containernet.term import makeTerm

from fanet_utils import get_sawtooth_destination, initialize_sawtooth, validate_scenario, kill_containers, \
    kill_process, set_sawtooth_location, set_rest_location, setup_network, time_stamp


def simulate(iterations_count: int = 30,
             wait_time_in_seconds: int = 5,
             skip_cli = False):
    
    iterations_count = int(iterations_count)
    wait_time_in_seconds = int(wait_time_in_seconds)
    setLogLevel('info')
    ports = [4004, 8008, 8800, 5050, 3030, 5000]
    docker_image = "containernet_example:sawtoothAll"
    
    os.system('cd examples/example-containers && ./build.sh')
    
    info( time_stamp() + '*** Starting monitors\n')
    grafana = subprocess.Popen(
        ["sh", "start_monitor.sh"], stdout=subprocess.PIPE)
    
    time.sleep(wait_time_in_seconds/2)

    net = Containernet()

    info(time_stamp() + '*** Adding base station\n')

    bs1 = net.addStation('base1',
                         ip='10.0.0.1',
                         mac='00:00:00:00:00:00',
                         cls=DockerSta,
                         dimage=docker_image,
                         ports=ports,
                         port_bindings={88: 8008, 8008: 88},
                         volumes=["/tmp/base1/data:/data"])

    info(time_stamp() + '*** Adding docker drones\n')

    # Intel Aero Ready to Fly Drone processor
    d1 = net.addStation('drone1',
                        ip='10.0.0.249',
                        mac='00:00:00:00:00:01',
                        cls=DockerSta,
                        dimage=docker_image,
                        ports=ports,
                        volumes=["/tmp/drone1/data:/data"],
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
                        volumes=["/tmp/drone2/data:/data"],
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
                        volumes=["/tmp/drone3/data:/data"],
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
                        volumes=["/tmp/drone4/data:/data"],
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
                        volumes=["/tmp/drone5/data:/data"],
                        mem_limit=3900182016,
                        cpu_shares=10,
                        cpu_period=50000,
                        cpu_quota=10000,
                        position='20,60,10')

    setup_network(net, bs1, d1, d2, d3, d4, d5)

    info(time_stamp() + '*** Starting Sawtooth on the Base Station ***\n')
    initialize_sawtooth(False, 0, False, bs1)

    info(time_stamp() + '*** Starting Sawtooth on the Drones ***\n')
    initialize_sawtooth(False, 0, False, d1, d2, d3, d4)

    if not skip_cli:
        info(time_stamp() + '*** Start drone terminals\n')
        makeTerm(bs1, cmd="bash")
        makeTerm(d1, cmd="bash")
        makeTerm(d2, cmd="bash")
        makeTerm(d3, cmd="bash")
        makeTerm(d4, cmd="bash")

    info(time_stamp() + '*** Waiting until the the Sawtooth peer connection\n')
    time.sleep(20)
    # info(time_stamp() + "*** Configure the node position\n")
    # setNodePosition = 'python {}/setNodePosition.py '.format(path) + sta_drone_send + ' &'
    # os.system(setNodePosition)
    
    # Common variables
    sc06_coord = '06'
    sc07_coord = '07'
    sc08_coord = '08 08 08'
    sc09_coord = '09 09 09'
    sc10_coord = '10'
    expected_sc06 = '60606'
    expected_sc07 = '70707'
    expected_sc10 = '101010'
    
    ################################### SCENARIO 06 ###################################
    info(time_stamp() + "*** Scenario 6: BS1 sends the new coordinates and the Sawtooth"\
            " network validates the update of the information\n")
    set_sawtooth_location(bs1, sc06_coord, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc06, get_destinations(d1, d2, d3, d4))
        
    ################################### SCENARIO 07 ###################################
    info(time_stamp() + "*** Scenario 7: Drone 3 need to rearrange the coordinates and"\
            " the Sawtooth network validates the update of the information\n")
    set_sawtooth_location(d3, sc07_coord, iterations=iterations_count, interval=wait_time_in_seconds)
    validate_scenario(net, expected_sc07, get_destinations(d1, d2, d3, d4))

    ################################### SCENARIO 08 ###################################
    info(time_stamp() + "*** Scenario 8: A compromised Drone in the FANET tries to send"\
        " a false destination update command to the other UAVs using the"\
            " unprotected REST Interface, without the possibility to"\
                " validate the information with the BS1\n")
    set_rest_location(d5, iterations_count, wait_time_in_seconds, target='10.0.0.249', coordinates=sc08_coord)
    validate_scenario(net, expected_sc07, get_destinations(d1, d2, d3, d4))
    
    ################################### SCENARIO 09 ###################################
    info(time_stamp() + "*** Scenario 9: BS1 validator is faulty and a compromised base" \
        " station joins the network tries to change the destination coordinates\n")
    os.system('docker container rm mn.base1 --force')
    bs2 = start_bs2_station(net)
    if not skip_cli:
        makeTerm(bs2, cmd="bash")
    set_rest_location(bs2, iterations_count, wait_time_in_seconds, '10.0.0.250', coordinates=sc09_coord)
    validate_scenario(net, expected_sc07, get_destinations(d1, d2, d3, d4))

    ################################### SCENARIO 10 ###################################
    info(time_stamp() + "*** Scenario 10: The connection with BS1 is lost and Drone 2"\
        " has to rearrange its coordinates\n")
    set_sawtooth_location(d2, sc10_coord, iterations=iterations_count, interval=wait_time_in_seconds)
    
    validate_scenario(net, expected_sc10, get_destinations(d1, d2, d3, d4))
    save_sawtooth_logs(d1, d2, d3, d4)
    
    if not skip_cli:
        info(time_stamp() + '*** Running CLI\n')
        CLI(net)

    info(time_stamp() + '*** Stopping network\n')
    kill_process()
    net.stop()


def start_bs2_station(net):
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
                
    return bs2

    
def save_sawtooth_logs(*args):
    for node in args:
        node.cmd('mkdir /data/sawtooth/ && cp /var/log/sawtooth/* /data/sawtooth/')

    
def get_destinations(d1, d2, d3, d4):
    return get_sawtooth_destination(d1),get_sawtooth_destination(d2),get_sawtooth_destination(d3),get_sawtooth_destination(d4)


if __name__ == '__main__':
    setLogLevel('info')
    # Killing old processes
    kill_process()
    kill_containers()
    
    if len(sys.argv) == 3 and sys.argv[0] is not 'sudo':
        skip_cli = True
        print('iterations: ' + sys.argv[1])
        print('wait time: ' + sys.argv[2])
        simulate(sys.argv[1], sys.argv[2], skip_cli)
    else:
        simulate()
