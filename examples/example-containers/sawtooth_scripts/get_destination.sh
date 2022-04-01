#!/bin/bash
if [ ! -d "/data/" ]; then
    mkdir /data
fi
intkey list > /data/locations.log