import codecs, time, socket
import encodings
import logging
import os
import pandas as pd
from flask import Flask, json, request

logging.basicConfig(filename='/data/server.log', encoding='utf-8', level=logging.DEBUG)
locations = [{"latitude": 0, "longitude": 0, "heigth": 0, 'timestamp': time.time()}]

api = Flask(__name__)

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

def propagate_message(new_coordinates):
    fanet_hosts = open('/rest/drones.json')
    json_array = json.load(fanet_hosts)
    drones_ip_list = []
    localhost_ip = extract_ip()
    for item in json_array:
        if item['address'] != localhost_ip:
            drones_ip_list.append(item['address'])
    logging.info('Propagating the message to the following hosts: ' + str(drones_ip_list))

    for drone_ip in drones_ip_list:
        logging.info('Sending coordinates ' + str(new_coordinates) + ' to host' + str(drone_ip))
        os.system('python /rest/client.py '
                + drone_ip + ' '
                + new_coordinates['latitude'] + ' '
                + new_coordinates['longitude'] + ' '
                + new_coordinates['heigth'])

@api.route('/locations', methods=['GET', 'POST'])
def handle_locations():
    if request.method == 'POST':
        locations.append(request.get_json())
        print (locations)
        df = pd.read_json(json.dumps(locations))
        df.to_csv('/data/locations.csv')
        with open('/data/locations.json', 'wb') as f:
            json.dump(locations, codecs.getwriter('utf-8')(f), ensure_ascii=False)
        propagate_message(request.get_json())
        return json.dumps(locations)
    return json.dumps(locations)

if __name__ == '__main__':
    api.run(host='0.0.0.0')