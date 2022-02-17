#!/usr/bin/env python3
import logging
import requests, sys, json, time

def post_data(address, lat, longi, hei, propagate=0):
    logging.basicConfig(filename="/data/locationClient.log",
                    filemode='a',
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    level=logging.DEBUG)
                    
    payload = {'latitude': lat, 'longitude': longi, 'heigth': hei, 'timestamp': time.time()}
    headers = {'Content-Type': 'application/json'}
    if propagate == 'True':
        logging.info('Propagating coordinates')
        url = "http://" + address + ":5000/propagate"
    else:
        logging.info('Adding coordinates')
        url = "http://" + address + ":5000/locations"
    result = requests.post(url, data=json.dumps(payload), headers=headers)
    logging.info(url)
    logging.info(payload)
    logging.info(headers)
    logging.info(result)

if __name__ == '__main__':
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print('Unable to add new coordinates')
        print('Try: client.py <host> <latitude> <longitude> <height>')
        print('Example: client.py 127.0.0.1 -27.1234 45.553435 100')
        quit()
    if len(sys.argv) == 6:
        post_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        post_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])