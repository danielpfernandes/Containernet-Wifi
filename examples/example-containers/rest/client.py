import requests, sys, json, time
def post_data(address, lat, longi, hei):
    payload = {'latitude': lat, 'longitude': longi, 'heigth': hei, 'timestamp': time.time()}
    headers = {'Content-Type': 'application/json'}
    url = "http://" + address + ":5000/locations"
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print('Adding coordinates')
    print(url)
    print(payload)
    print(headers)
    print(r)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Unable to add new coordinates')
        print('Try: client.py <host> <latitude> <longitude> <height>')
        print('Example: client.py 127.0.0.1 -27.1234 45.553435 100')
        quit()
    post_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])