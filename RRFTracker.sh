#!/bin/sh
PATH='/opt/RRFTracker_Spotnik/'
PATH_SCRIPT='/opt/RRFTracker_Spotnik/RRFTracker.py'
PATH_PID='/var/log'

case "$1" in
    start)
        /bin/echo "Starting RRFTracker: I2C 0"
        cd $PATH
        /usr/bin/nohup /usr/bin/python $PATH_SCRIPT --i2c-port 0 --display ssd1327 --display-height 128 --room SCAN --callsign F4HWN > $PATH_PID/RRFTracker_Spotnik_0.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_0.pid
        /bin/echo "Starting RRFTracker: I2C 1"
        cd $PATH
        /usr/bin/nohup /usr/bin/python $PATH_SCRIPT --i2c-port 1 --display ssd1327 --display-height 128 --room SCAN --callsign F1ZPX > $PATH_PID/RRFTracker_Spotnik_1.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_1.pid
        ;;
    stop) 
        /bin/echo "Stopping RRFTracker: I2C 0"
        /bin/kill `/bin/cat $PATH_PID/RRFTracker_Spotnik_0.pid`
        /bin/echo "Stopping RRFTracker: I2C 1"
        /bin/kill `/bin/cat $PATH_PID/RRFTracker_Spotnik_1.pid`
        ;;
esac