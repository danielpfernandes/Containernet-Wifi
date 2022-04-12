#!/usr/bin/env python3
import codecs
import logging
import requests
import sys
import json

from datetime import datetime

LOCATION_CLIENT_LOG_PATH = "/data/locationClient.log"
VALIDATION_FILE_PATH = '/tmp/currentDestination.json'
BASE_STATION_IP = '10.0.0.1'
LOCALHOST_IP = '0.0.0.0'
LATITUDE_KEY = 'latitude'
LONGITUDE_KEY = 'longitude'
TIMESTAMP_KEY = 'timestamp'


def coord_time_stamp():
    return str(datetime.now().strftime('%Y-%m-%dT%H-%M-%S'))


def post_data(address, lat, longi, propagate=0):
    logging.basicConfig(filename=LOCATION_CLIENT_LOG_PATH,
                        filemode='a',
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        level=logging.DEBUG)

    # Prepare the Request payload
    payload = {TIMESTAMP_KEY: coord_time_stamp(), LATITUDE_KEY: lat, LONGITUDE_KEY: longi}
    headers = {'Content-Type': 'application/json'}

    # If the purpose is to propagate to others nodes, then the endpoint /propagate should be used
    if propagate == 'True':
        logging.info('Propagating coordinates')
        url = "http://" + address + ":5000/propagate"

    # Otherwise, saves the coordinate only in the target host
    else:
        logging.info('Adding coordinates')
        url = "http://" + address + ":5000/locations"

    # Write the coordinates in a temporary file for validation
    with open(VALIDATION_FILE_PATH, 'wb') as f:
        json.dump(payload, codecs.getwriter('utf-8')(f), ensure_ascii=False)

    # POST the Request
    result = requests.post(url, data=json.dumps(payload), headers=headers)
    logging.info(url)
    logging.info(payload)
    logging.info(headers)
    logging.info(result)


if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print('Unable to add new coordinates')
        print('Try: setLocation.py <host> <latitude> <longitude>')
        print('Example: setLocation.py 127.0.0.1 -27.1234 45.553435')
        quit()
    if len(sys.argv) == 5:
        post_data(sys.argv[1], sys.argv[2],
                  sys.argv[3], sys.argv[4])
    else:
        post_data(sys.argv[1], sys.argv[2], sys.argv[3])
