import os
import sys
import time

from datetime import datetime
from mininet.log import info
from mn_wifi.link import adhoc

from containernet.net import Containernet
from containernet.term import makeTerm

cmd_keep_alive = '; bash'


def time_stamp() -> str:
    return str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%s'))


def add_link(net: Containernet, node: any):
    net.addLink(node, cls=adhoc, intf=str(node.name) + '-wlan0',
                ssid='adhocNet', proto='batman_adv',
                mode='g', channel=5, ht_cap='HT40+')


def setup_network(net: Containernet, *argv):
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("\n*** Configuring wifi nodes\n")

    net.configureWifiNodes()

    for node in argv:
        add_link(net, node)

    info(time_stamp() + '*** Starting network\n')
    net.build()
    net.start()

    # nodes = net.stations
    # telemetry(nodes=nodes, single=True, data_type='position')

    sta_drone = []
    for n in net.stations:
        sta_drone.append(n.name)
    sta_drone_send = ' '.join(map(str, sta_drone))

    # # set_socket_ip: localhost must be replaced by ip address
    # # of the network interface of your system
    # # The same must be done with socket_client.py
    info(time_stamp() + '*** Starting Socket Server\n')
    net.socketServer(ip='127.0.0.1', port=12345)

    # info("*** Starting CoppeliaSim\n")
    path = os.path.dirname(os.path.abspath(__file__))
    # os.system('{}/CoppeliaSim_Edu_V4_1_0_Ubuntu/coppeliaSim.sh -s {}'
    #             '/simulation.ttt -gGUIITEMS_2 &'.format(path, path))
    # time.sleep(10)

    info("\n*** Perform a simple test\n")
    simple_test = 'python {}/simpleTest.py '.format(
        path) + sta_drone_send + ' &'
    os.system(simple_test)


def set_rest_location(
        station: any, iterations=10, interval=10, target='10.0.0.249', coordinates='0 0 0'):
    """Set the drone location

    Args:
        station (any): Mininet node (source station)
        iterations (int, optional): Numbers of iterations to run the command. Defaults to 10.
        interval (int, optional): Interval in seconds between each iteration. Defaults to 10.
        target (str, optional): Target node (drone). Defaults to '10.0.0.249'.
        coordinates (str, optional):
            Coordinates in format <latitude> <longitude> <altitude>. Defaults to '0 0 0'.
    """
    for number in range(iterations):
        station.cmd('python /rest/setLocation.py '
                    + target + ' '
                    + coordinates + ' True &')
        time.sleep(interval)
        info(time_stamp() + " Iteration number " + str(number + 1) + " of " + str(iterations) + "\n")


def initialize_sawtooth(should_open_terminal=False, wait_time_in_seconds: int = 0,
                        keep_terminal_alive=False, *args):
    for node in args:
        start_validator(node, should_open_terminal,
                        wait_time_in_seconds, keep_terminal_alive)
        start_rest_api(node, should_open_terminal, keep_terminal_alive)
        start_transaction_processors( node,
            should_open_terminal, keep_terminal_alive)
        start_consensus_mechanism(node, should_open_terminal, keep_terminal_alive)


def start_validator(node: any,
                    should_open_terminal: bool = False,
                    wait_time_in_seconds: int = 2,
                    keep_terminal_alive=False):
    """Start the Validator

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    command = 'bash /sawtooth_scripts/validator.sh ' + station_name

    info(time_stamp() + '*** Generating sawtooth keypair for ' + station_name + ' ***\n')

    if station_name is 'base1':
        info(time_stamp() + '*** Create the Genesis Block on Base Station\n')
        info(time_stamp() + '*** Create a batch to initialize the consensus settings on the Base Station\n')
        info(time_stamp() + '*** Combining batches in one genesis batch on Base Station ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' Validator', cmd=command)
        time.sleep(wait_time_in_seconds)
    else:
        node.cmd(command + ' &')
        time.sleep(wait_time_in_seconds)


def start_rest_api(node: any,
                   should_open_terminal: bool = False,
                   keep_terminal_alive=False):
    """Start the REST API

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command = 'sudo -u sawtooth sawtooth-rest-api -v --connect tcp://' + station_ip + ':4004'

    info(time_stamp() + '*** Start REST API for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' REST API', cmd=command)
    else:
        node.cmd(command + ' &')


def start_transaction_processors(node: any,
                                 should_open_terminal: bool = False,
                                 wait_time_in_seconds: int = 0,
                                 keep_terminal_alive=False):
    """Start the transaction processors

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional):
            If True, opens a new terminal for each processor. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """

    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command_settings_tp = 'sudo -u sawtooth settings-tp -v --connect tcp://' + \
                        station_ip + ':4004'
    command_intkey_tp = 'sudo -u sawtooth intkey-tp-python -v --connect tcp://' + \
                        station_ip + ':4004'
    command_poet_validator_registry_tp = 'sudo -u sawtooth poet-validator-registry-tp -v --connect tcp://' + \
                        station_ip + ':4004'

    info(time_stamp() + '*** Start Transaction Processors for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command_settings_tp += cmd_keep_alive
            command_intkey_tp += cmd_keep_alive
            command_poet_validator_registry_tp += cmd_keep_alive

        makeTerm(node=node, title=station_name +
                                ' Settings Transaction Processor', cmd=command_settings_tp)
        time.sleep(wait_time_in_seconds)
        makeTerm(node=node, title=station_name +
                                ' Intkey Transaction Processor', cmd=command_intkey_tp)
        time.sleep(wait_time_in_seconds)
        makeTerm(node=node, title=station_name +
                                ' PoET Validator Registry Transaction Processor',
                                cmd=command_poet_validator_registry_tp)
    else:
        node.cmd(command_settings_tp + ' &')
        time.sleep(wait_time_in_seconds)
        node.cmd(command_intkey_tp + ' &')
        time.sleep(wait_time_in_seconds)
        node.cmd(command_poet_validator_registry_tp + ' &')


def start_consensus_mechanism(node: any,
                              should_open_terminal: bool = False,
                              keep_terminal_alive=False):
    """Start the consensus engine

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """

    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command = 'poet-engine -vv --connect tcp://localhost:5050 --component tcp://' + \
                        station_ip + ':4004'

    info(time_stamp() + '*** Start Consensus Engine for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name +
                                ' Consensus Mechanism', cmd=command + cmd_keep_alive)
    else:
        node.cmd(command + ' &')


def set_sawtooth_location(station: any,
                          coordinate: int,
                          iterations=10,
                          interval=10):
    """Sets the coordinates to the destination of the FANET

    Args:
        node (any): Mininet node
        latitude (int): Latitude
        longitude (int): Longitude
        altitude (int): Altitude
    """
    for number in range(iterations):
        station.cmd("intkey set " + str(time.time()) + " " + str(coordinate) + str(coordinate) + str(coordinate))
        time.sleep(interval)
        info(time_stamp() + " Iteration number " + str(number + 1) + " of " + str(iterations) + "\n")



def get_sawtooth_destination(node: any) -> str:
    """Get the coordinates stored in the node transactions
    
    Args:
        node (any): Mininet node

    Returns:
        str: The coordinate registries
    """
    node.cmd("sh /sawtooth_scripts/get_destination.sh")

    return node.cmd("cat /data/locations.log")


def is_simulation_successful(expected_coord, coordinates) -> bool: 
    
    for result in coordinates:
        expected_result = expected_coord in result
        if expected_result is False:
            return expected_result
    
    return expected_result


def validate_scenario(net, expected_coord, coordinates) -> bool:
    for coord in coordinates:
        info('Node coordinates: \n' + str(coord) + '\n')
    if is_simulation_successful(expected_coord, coordinates):
        info(time_stamp() + " ******************** SIMULATION SUCCESSFULL! ********************\n")
    else:
        info(time_stamp() + " ******************** SIMULATION FAILED! ********************\n")
        kill_process()
        net.stop()
        sys.exit(1)


def kill_process():
    # os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')


def kill_containers():
    os.system('kill -TERM $(pgrep -f prometheus)')
    os.system('rm examples/uav/data/*')
    os.system('rm -rf /tmp/poet-shared')
    os.system('docker container rm grafana cadvisor mn.drone1 '\
        'mn.drone2 mn.drone3 mn.drone4 mn.drone5 mn.base1 mn.base2 --force')
    os.system('service docker restart')
