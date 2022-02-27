#!/usr/bin/env python3
import subprocess , requests, logging, codecs, time, socket
import pandas as pd
from crypt import methods
from flask import Flask, json, request
from numpy import empty

logging.basicConfig(filename="/data/locationRestServer.log",
                    filemode='a',
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    level=logging.DEBUG)

locations = [{"latitude": 0, "longitude": 0, "heigth": 0, 'timestamp': time.time()}]
baseStationURL = 'http://10.0.0.1/validate'

api = Flask(__name__)
api.config['DEBUG'] = True

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.0.0.1', 5000))
        IP = st.getsockname()[0]
    except Exception:
        print('Could not get the iface address. Using localhost as default')
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

localhost_ip = extract_ip()

def propagate_message(new_coordinates):
    fanet_hosts = open('/rest/drones.json')
    json_array = json.load(fanet_hosts)
    drones_ip_list = []
    for item in json_array:
        if item['address'] != localhost_ip:
            drones_ip_list.append(item['address'])
    logging.info('Propagating the message to the following hosts: ' + str(drones_ip_list))

    for drone_ip in drones_ip_list:
        logging.info('Sending coordinates ' + str(new_coordinates) + ' to host' + str(drone_ip))
        result = subprocess.Popen('setLocation.py '
                + drone_ip + ' '
                + new_coordinates['latitude'] + ' '
                + new_coordinates['longitude'] + ' '
                + new_coordinates['heigth'], shell=True, stdout=subprocess.PIPE)
        logging.debug(result)

@api.route('/locations', methods=['GET', 'POST'])
def handle_locations():
    if request.method == 'POST':
        locations.append(request.get_json())
        print (locations)
        df = pd.read_json(json.dumps(locations))
        df.to_csv('/data/locations.csv')
        with open('/data/locations.json', 'wb') as f:
            json.dump(locations, codecs.getwriter('utf-8')(f), ensure_ascii=False)
        return json.dumps(locations)
    return json.dumps(locations)

@api.route('/propagate', methods=['POST'])
def propagate_locations():
    currentLocation = requests.get(baseStationURL)
    if currentLocation.status_code == 200 and currentLocation.json != request.get_json():
        error = 'Propagation of coordinates does not match with the base station information. Validation failed'
        logging.warning(error)
        return json.dumps('[message: ${error}')
    locations.append(request.get_json())
    print (locations)
    df = pd.read_json(json.dumps(locations))
    df.to_csv('/data/locations.csv')
    with open('/data/locations.json', 'wb') as f:
        json.dump(locations, codecs.getwriter('utf-8')(f), ensure_ascii=False)
    propagate_message(request.get_json())
    return json.dumps(locations)

@api.route('/validate', methods=['GET'])
def validate_locations():
    with open('/tmp/currentDestination.json', 'r') as f:
        return json.dumps(f.read)

if __name__ == '__main__':
    api.run(host='0.0.0.0')