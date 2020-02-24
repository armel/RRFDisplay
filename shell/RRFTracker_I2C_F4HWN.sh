#!/bin/sh
PATH_SCRIPT='/opt/RRFTracker_Spotnik/RRFTracker.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFTracker: I2C 0"
        nohup python $PATH_SCRIPT --interface i2c --i2c-port 0 --display ssd1327 --display-height 128 --display-theme gray.cfg --follow F4HWN > $PATH_PID/RRFTracker_Spotnik_0.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_0.pid
        ;;
    stop) 
        echo "Stopping RRFTracker: I2C 0"
        kill `cat $PATH_PID/RRFTracker_Spotnik_0.pid`
        ;;
esac