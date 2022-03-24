from distutils.log import error
from mininet.log import info
import os
import time

from containernet.term import makeTerm

cmd_keep_alive = '; bash'

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


def initialize_sawtooth(node: any, should_open_terminal=False, wait_time_in_seconds: int = 2, keep_terminal_alive = False):
    start_validator(node, should_open_terminal, wait_time_in_seconds, keep_terminal_alive)
    start_rest_api(node, should_open_terminal, keep_terminal_alive)
    start_transaction_processors(node, should_open_terminal, keep_terminal_alive)
    start_consensus_mecanism(node, should_open_terminal, keep_terminal_alive)


def start_validator(node: any, should_open_terminal: bool = False, wait_time_in_seconds: int = 2, keep_terminal_alive = False):
    """Start the Validator

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
        wait_time_in_seconds (int, optional): Wait time in seconds before leaving the command
    """
    station_name = str(node.name)
    command = 'bash /sawtooth_scripts/validator.sh ' + station_name
    
    info('\n*** Generating sawtooth keypairs for ' + station_name + ' ***\n')
    
    if station_name is 'base1':
        info('\n*** Create the Genesis Block on Base Station\n')
        info('\n*** Create a batch to initialize the consensus settings on the Base Station\n')
        info('\n*** Combining batches in one genesis bath on Base Station ***\n')
    
    if should_open_terminal:
        if keep_terminal_alive: command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' Validator', cmd=command)
        time.sleep(wait_time_in_seconds)
    else:
        node.cmd(command + ' &')
        time.sleep(wait_time_in_seconds)


def start_rest_api(node: any, should_open_terminal: bool = False, keep_terminal_alive = False):
    """Start the REST API

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
    """
    station_name = str(node.name)
    command = 'sudo -u sawtooth sawtooth-rest-api -v --connect 127.0.0.1:4004'
    
    info('\n*** Start REST API for ' + station_name + ' ***\n')
    
    if should_open_terminal:
        if keep_terminal_alive: command += cmd_keep_alive
        makeTerm(node=node, title=station_name + ' REST API', cmd=command)
    else:
        node.cmd(command + ' &')


def start_transaction_processors(node: any, should_open_terminal: bool = False, wait_time_in_seconds: int = 5, keep_terminal_alive = False):
    """Start the transacion processors

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal for each processor. Defaults to False.
    """
    station_name = str(node.name)
    command_transaction = 'sudo -u sawtooth settings-tp -v'
    command_processor = 'sudo -u sawtooth intkey-tp-python -v'
    
    info('\n*** Start Transaction Processors for ' + station_name + ' ***\n')
    
    if should_open_terminal:
        if keep_terminal_alive: command += cmd_keep_alive
        makeTerm(node=node, title=station_name +
                 ' Transaction Settings', cmd=command_transaction)
        time.sleep(wait_time_in_seconds)
        makeTerm(node=node, title=station_name +
                 ' Intkey Processor', cmd=command_processor)
    else:
        node.cmd(command_transaction + ' &')
        time.sleep(wait_time_in_seconds)
        node.cmd(command_processor + ' &')


def start_consensus_mecanism(node: any, should_open_terminal: bool = False, keep_terminal_alive = True):
    """Start the consensus engine

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
    """
    station_name = str(node.name)
    command = 'sudo -u sawtooth pbft-engine -vv --connect tcp://localhost:5050'
    
    info('\n*** Start Consensus Engine for ' + station_name + ' ***\n')
    
    if should_open_terminal:
        if keep_terminal_alive: command += cmd_keep_alive
        makeTerm(node=node, title=station_name +
                 ' Consensus Mecanism', cmd=command + cmd_keep_alive)
    else:
        node.cmd(command + ' &')


def generate_keypairs(node: any) -> str:
    """Create User and Validator keypairs

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
    """Create batch to initilize the consensus settings.
    Args:
        node (any): Mininet node
        public_key (dict): Dictionary with the network public keys
    """
    pbft_members = '\'["'+public_key['d1']+'","'+public_key['d2']+'","'+public_key['d3'] + \
        '","'+public_key['d4']+'","'+public_key['d5'] + \
        '","'+public_key['bs1']+'"]\''
    node.cmd("sawset proposal create --key $HOME/.sawtooth/keys/root.priv \
    -o /tmp/config-consensus.batch \
    sawtooth.consensus.algorithm.name=pbft \
    sawtooth.consensus.algorithm.version=1.0 \
    sawtooth.publisher.max_batches_per_block=1200 \
    sawtooth.consensus.pbft.members=" + pbft_members)


def kill_process():
    #os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')