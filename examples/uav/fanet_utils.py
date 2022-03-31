import os
import time

from mininet.log import info
from mn_wifi.link import adhoc

from containernet.net import Containernet
from containernet.term import makeTerm

cmd_keep_alive = '; bash'


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

    info('\n*** Starting network\n')
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
    info('\n*** Starting Socket Server\n')
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


def set_location(
        station: any, iterations=10, interval=10, target='10.0.0.249', coordinates='0 0 0'):
    """Set the drone location

    Args:
        station (any): Mininet node (source station)
        iterations (int, optional): Numbers of iterations to run the command. Defaults to 10.
        interval (int, optional): Interval in seconds between each iteration. Defaults to 10.
        target (str, optional): Target node (drone). Defaults to '10.0.0.249'.
        coordinates (str, optional): Coordinates in format <latitude> <longitude> <altitude>. Defaults to '0 0 0'.
    """
    for number in range(iterations):
        station.cmd('python /rest/setLocation.py '
                    + target + ' '
                    + coordinates + ' True &')
        time.sleep(interval)
        print("Iteration number " + str(number + 1) + " of " + str(iterations))


def initialize_sawtooth(node: any, should_open_terminal=False, wait_time_in_seconds: int = 2,
                        keep_terminal_alive=False):
    start_validator(node, should_open_terminal,
                    wait_time_in_seconds, keep_terminal_alive)
    start_rest_api(node, should_open_terminal, keep_terminal_alive)
    start_transaction_processors(
        node, should_open_terminal, keep_terminal_alive)
    start_consensus_mechanism(node, should_open_terminal, keep_terminal_alive)


def start_validator(node: any, should_open_terminal: bool = False,
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

    info('\n*** Generating sawtooth keypair for ' + station_name + ' ***\n')

    if station_name is 'base1':
        info('\n*** Create the Genesis Block on Base Station\n')
        info('\n*** Create a batch to initialize the consensus settings on the Base Station\n')
        info('\n*** Combining batches in one genesis bath on Base Station ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' Validator', cmd=command)
        time.sleep(wait_time_in_seconds)
    else:
        node.cmd(command + ' &')
        time.sleep(wait_time_in_seconds)


def start_rest_api(node: any, should_open_terminal: bool = False, keep_terminal_alive=False):
    """Start the REST API

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command = 'sudo -u sawtooth sawtooth-rest-api -v --connect tcp://' + station_ip + ':4004'

    info('\n*** Start REST API for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' REST API', cmd=command)
    else:
        node.cmd(command + ' &')


def start_transaction_processors(node: any, should_open_terminal: bool = False, wait_time_in_seconds: int = 5,
                                 keep_terminal_alive=False):
    """Start the transaction processors

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal for each processor. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    station_ip = str(node.params.get('ip'))
    command_transaction = 'sudo -u sawtooth settings-tp -v --connect tcp://' + \
                          station_ip + ':4004'
    command_processor = 'sudo -u sawtooth intkey-tp-python -v --connect tcp://' + \
                        station_ip + ':4004'

    info('\n*** Start Transaction Processors for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command_transaction += cmd_keep_alive
            command_processor += cmd_keep_alive

        makeTerm(node=node, title=station_name +
                                  ' Transaction Settings', cmd=command_transaction)
        time.sleep(wait_time_in_seconds)
        makeTerm(node=node, title=station_name +
                                  ' Intkey Processor', cmd=command_processor)
    else:
        node.cmd(command_transaction + ' &')
        time.sleep(wait_time_in_seconds)
        node.cmd(command_processor + ' &')


def start_consensus_mechanism(node: any, should_open_terminal: bool = False, keep_terminal_alive=False):
    """Start the consensus engine

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        keep_terminal_alive (bool, optional): Leave the terminal open if it fails
    """
    station_name = str(node.name)
    command = 'sudo -u sawtooth pbft-engine -vv --connect tcp://localhost:5050'

    info('\n*** Start Consensus Engine for ' + station_name + ' ***\n')

    if should_open_terminal:
        if keep_terminal_alive:
            command += cmd_keep_alive
        makeTerm(node=node, title=station_name +
                                  ' Consensus Mechanism', cmd=command + cmd_keep_alive)
    else:
        node.cmd(command + ' &')


def generate_keypair(node: any) -> str:
    """Create User and Validator keypair

    Args:
        node (any): Mininet node

    Returns:
        str: Validator public key
    """

    node.cmd("sawtooth keygen")
    node.cmd("sawadm keygen")
    key = node.cmd("cat /etc/sawtooth/keys/validator.pub")
    return key.replace('\r\n', '')


def create_batch_settings(node, public_key: dict):
    """Create batch to initialize the consensus settings.
    Args:
        node (any): Mininet node
        public_key (dict): Dictionary with the network public keys
    """
    pbft_members = '\'["' + public_key['d1'] + '","' + public_key['d2'] + '","' + public_key['d3'] + \
                   '","' + public_key['d4'] + '","' + public_key['d5'] + \
                   '","' + public_key['bs1'] + '"]\''
    node.cmd("sawset proposal create --key $HOME/.sawtooth/keys/root.priv \
    -o /tmp/config-consensus.batch \
    sawtooth.consensus.algorithm.name=pbft \
    sawtooth.consensus.algorithm.version=1.0 \
    sawtooth.publisher.max_batches_per_block=1200 \
    sawtooth.consensus.pbft.members=" + pbft_members)


def set_destination(node: any, latitude: int, longitude: int, altitude: int):
    """Sets the coordinates to the destination of the FANET

    Args:
        node (any): Mininet node
        latitude (int): Latitude
        longitude (int): Longitude
        altitude (int): Altitude
    """
    node.cmd("intkey set " + str(time.time()) + " " + str(latitude) + str(longitude) + str(altitude))


def get_destination(node: any) -> str:
    """Get the coordinates stored in the node transactions
    
    Args:
        node (any): Mininet node

    Returns:
        str: The coordinate registries
    """
    node.cmd("sh /sawtooth_scripts/get_destination.sh")

    return node.cmd("cat /data/locations.log")


def kill_process():
    # os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')
    os.system('rm -rf /tmp/pbft-shared')
