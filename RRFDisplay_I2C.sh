#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

case "$1" in
    start)
        echo "Starting RRFDisplay: I2C 0"
        nohup python3 $PATH_SCRIPT --interface i2c --i2c-port 0 --display ssd1327 --display-height 128 --display-theme gray.cfg --follow F1ZPX > $PATH_PID/RRFDisplay_0.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_0.pid
        ;;
    stop) 
        echo "Stopping RRFDisplay: I2C 0"
        kill `cat $PATH_PID/RRFDisplay_0.pid`
        ;;
esac