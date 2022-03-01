#!/usr/bin/env python3
import subprocess
import requests
import logging
import codecs
import time
import socket
import pandas as pd
from flask import Flask, json, request

LOCATION_REST_SERVER_LOG_PATH = "/data/locationRestServer.log"
LOCATION_DATA_CSV_PATH = '/data/locations.csv'
LOCATION_DATA_JSON_PATH = '/data/locations.json'
VALIDATION_FILE_PATH = '/tmp/currentDestination.json'
DRONES_IP_ADDRESSES_JSON_PATH = '/rest/drones.json'
BASE_STATION_IP = '10.0.0.1'
LOCALHOST_IP = '0.0.0.0'
LATITUDE_KEY = 'latitude'
LONGITUDE_KEY = 'longitude'
ALTITUDE_KEY = 'altitude'
TIMESTAMP_KEY = 'timestamp'


# Places the log files into /data/ directory
logging.basicConfig(filename=LOCATION_REST_SERVER_LOG_PATH,
                    filemode='a',
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    level=logging.DEBUG)

locations = [{LATITUDE_KEY: 0, LONGITUDE_KEY: 0,
              ALTITUDE_KEY: 0, TIMESTAMP_KEY: time.time()}]

api = Flask(__name__)
api.config['DEBUG'] = True


def extract_ip():
    """
    Extracts the IP address of the runninh host in the network
    """
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Points to the base station to get the host IP
        st.connect((BASE_STATION_IP, 5000))
        IP = st.getsockname()[0]
    except Exception:
        print('Could not get the iface address. Using localhost as default')
        IP = LOCALHOST_IP
    finally:
        st.close()
    return IP


localhost_ip = extract_ip()


def propagate_message(new_coordinates):
    """
    Propagates the new coordinates to the other hosts that belongs to the network
    """

    # The file that contains the IP address from the hosts in the network
    fanet_hosts = open(DRONES_IP_ADDRESSES_JSON_PATH)
    json_array = json.load(fanet_hosts)
    drones_ip_list = []

    # Verifies all the hosts IP addresses and excludes the source host from the list
    for item in json_array:
        if item['address'] != localhost_ip:
            drones_ip_list.append(item['address'])
    logging.info(
        'Propagating the message to the following hosts: ' + str(drones_ip_list))

    # Send the new coordinates for each host
    for drone_ip in drones_ip_list:
        logging.info('Sending coordinates ' +
                     str(new_coordinates) + ' to host' + str(drone_ip))
        result = subprocess.Popen('setLocation.py '
                                  + drone_ip + ' '
                                  + new_coordinates[LATITUDE_KEY] + ' '
                                  + new_coordinates[LONGITUDE_KEY] + ' '
                                  + new_coordinates[ALTITUDE_KEY], shell=True, stdout=subprocess.PIPE)
        logging.debug(result)


def compare_coordinates(reference_host, request_info):
    """
    Compares the latitude, longitude and the altitude between the reference host and the request
        :param reference_host Reference host JSON files
        :param request_info Request content in JSON format
        Returns True if the values matches
    """
    return reference_host[LATITUDE_KEY] == request_info[LATITUDE_KEY] \
        and reference_host[LONGITUDE_KEY] == request_info[LONGITUDE_KEY] \
        and reference_host[ALTITUDE_KEY] == request_info[ALTITUDE_KEY]


def validate_coordinates_with_base_station(request_json, base_station_url):
    """
    Validates the coordinates before propagate the information to other hosts
        :request_json Request content in JSON format
        :base_station_url Base station validation REST API endpoint
        Returns True if the validation is sucessful
    """
    error_message = 'Propagation of coordinates does not match with the base station information. Validation failed'
    success_message = 'Base Station matches with the request. Validation sucessful!'

    logging.info('Retrieving destination coordinates from base station')
    current_location = requests.get(base_station_url)

    logging.info(current_location)
    logging.info('Base station response: ' + str(current_location.content))
    logging.info('New coordintates paylod' + str(request_json))

    if compare_coordinates(json.loads(current_location.content), request_json) and current_location.status_code == 200:
        logging.info(success_message)
        return True
    logging.error(error_message)
    return False


@api.route('/locations', methods=['GET', 'POST'])
def handle_locations():

    # If the request is a POST method, then it will store the coordinates into the location data files
    if request.method == 'POST':
        locations.append(request.get_json())
        print(locations)
        df = pd.read_json(json.dumps(locations))
        df.to_csv(LOCATION_DATA_CSV_PATH)
        with open(LOCATION_DATA_JSON_PATH, 'wb') as f:
            json.dump(locations, codecs.getwriter(
                'utf-8')(f), ensure_ascii=False)
        return json.dumps(locations)

    # If the request is a GET method, then it will return the coordinate history stored in the location data JSON file
    return json.dumps(locations)


def propagate(request):
    # Add the new coordinate in the JSON and CSV files
    locations.append(request.get_json())
    df = pd.read_json(json.dumps(locations))
    df.to_csv(LOCATION_DATA_CSV_PATH)
    with open(LOCATION_DATA_JSON_PATH, 'wb') as f:
        json.dump(locations, codecs.getwriter(
            'utf-8')(f), ensure_ascii=False)

    # Propagate the message to the other hosts in the network
    propagate_message(request.get_json())
    return json.dumps(locations)


@api.route('/propagate', methods=['POST'])
def propagate_locations():
    """
    Propagates the coordinatas change request using this REST API
    """

    # Validates if the new coordinates information matches with the values stored in the base station current request
    try:
        base_station_url = 'http://' + BASE_STATION_IP + ':5000/validate'
        if validate_coordinates_with_base_station(request.get_json(), base_station_url):
            propagate(request)

        # Fails if the validation does not match
        return 'Propagation failed', 500

    # If the connection with the base station is lost, show must go on :)
    except:
        error_message = 'Connection with the base station failed. '
        warning_message = '!!!!!!!!!!!!!!!! PROPAGATING INFORMATION WITHOUT VALIDATION !!!!!!!!!!!!!!'
        logging.error(error_message)
        logging.warning(warning_message)
        propagate(request)
        return error_message + warning_message, 203


@api.route('/validate', methods=['GET'])
def validate_locations():
    return json.dumps(json.load(open(VALIDATION_FILE_PATH)))


if __name__ == '__main__':
    api.run(host=LOCALHOST_IP)
