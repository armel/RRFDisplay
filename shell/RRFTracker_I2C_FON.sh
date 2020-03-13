#!/bin/sh
PATH_SCRIPT='/opt/RRFTracker_Spotnik/RRFTracker.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFTracker: I2C 1"
        nohup python $PATH_SCRIPT --interface i2c --i2c-port 1 --display sh1106 --display-height 64 --display-theme mono.cfg --follow FON > $PATH_PID/RRFTracker_Spotnik_1.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_1.pid
        ;;
    stop) 
        echo "Stopping RRFTracker: I2C 1"
        kill `cat $PATH_PID/RRFTracker_Spotnik_1.pid`
        ;;
esac