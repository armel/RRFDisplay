#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFDisplay: I2C 1"
        nohup python3 $PATH_SCRIPT --interface i2c --i2c-port 1 --display ssd1327 --display-height 128 --display-theme gray.cfg --follow FON > $PATH_PID/RRFDisplay_1.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_1.pid
        ;;
    stop) 
        echo "Stopping RRFDisplay: I2C 1"
        kill `cat $PATH_PID/RRFDisplay_1.pid`
        ;;
esac