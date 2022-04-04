#!/usr/bin/env python
import subprocess
import sys
    
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[0] is not 'sudo':
        skip_cli = True
        print('iterations: ' + sys.argv[1])
        print('wait time: ' + sys.argv[2])
        with open("output.log", "w+") as output:
            subprocess.call(["python", "./examples/uav/fanet_simulation_wifi_sawtooth.py", sys.argv[1] , sys.argv[2]], stdout=output)
    else:
        with open("output.log", "w+") as output:
            subprocess.call(["python", "./examples/uav/fanet_simulation_wifi_sawtooth.py"], stdout=output)