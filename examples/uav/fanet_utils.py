import os
import time

from containernet.term import makeTerm


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


def initialize_sawtooth(node: any, should_open_terminal=False):
    start_validator(node, should_open_terminal)
    start_rest_api(node, should_open_terminal)
    start_transaction_processors(node, should_open_terminal)
    start_consensus_mecanism(node, should_open_terminal)


def start_validator(node: any, should_open_terminal: bool = False):
    """Start the Validator

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
    """
    ip = str(node.params.get('ip'))
    peers = ["10.0.0.1", "10.0.0.249", "10.0.0.250",
             "10.0.0.251", "10.0.0.252", "10.0.0.253"]
    peers.remove(ip)
    command = 'sudo -u sawtooth sawtooth-validator \
        --bind component:tcp://127.0.0.1:4004 \
        --bind network:tcp://' + ip + ':8800 \
        --bind consensus:tcp://' + ip + ':5050 \
        --endpoint tcp://' + ip + ':8800 \
        --peers tcp://' + peers[0] + ':8800, tcp://' + peers[1] + ':8800, tcp://' + peers[2] + ':8800, tcp://' + peers[3] + ':8800, tcp://' + peers[4] + ':8800'
    if should_open_terminal:
        makeTerm(node=node, title=str(node.name) + ' Validator', cmd=command)
    else:
        node.cmd(command + ' &')


def start_rest_api(node: any, should_open_terminal: bool = False):
    """Start the REST API

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
    """
    command = 'sudo -u sawtooth sawtooth-rest-api -v'
    if should_open_terminal:
        makeTerm(node=node, title=str(node.name) + ' REST API', cmd=command)
    else:
        node.cmd(command + ' &')


def start_transaction_processors(node: any, should_open_terminal: bool = False):
    """Start the transacion processors

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal for each processor. Defaults to False.
    """
    command_transaction = 'sudo -u sawtooth settings-tp -v'
    command_processor = 'sudo -u sawtooth intkey-tp-python -v'
    if should_open_terminal:
        makeTerm(node=node, title=str(node.name) +
                 ' Transaction Settings', cmd=command_transaction)
        makeTerm(node=node, title=str(node.name) +
                 ' Intkey Processor', cmd=command_processor)
    else:
        node.cmd(command_transaction + ' &')
        node.cmd(command_processor + ' &')


def start_consensus_mecanism(node: any, should_open_terminal: bool = False):
    """Start the consensus engine

    Args:
        node (any): Mininet node
        should_open_terminal (bool, optional): If True, opens a new terminal. Defaults to False.
    """
    command = 'sudo -u sawtooth pbft-engine -vv --connect tcp://localhost:5050'
    if should_open_terminal:
        makeTerm(node=node, title=str(node.name) +
                 ' Consensus Mecanism', cmd=command)
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
    sawtooth.consensus.pbft.members=" + pbft_members)


def kill_process():
    #os.system('pkill -9 -f coppeliaSim')
    os.system('pkill -9 -f simpleTest.py')
    os.system('pkill -9 -f setNodePosition.py')
    os.system('rm examples/uav/data/*')