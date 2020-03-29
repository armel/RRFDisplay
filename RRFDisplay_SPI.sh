#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

case "$1" in
    start)
        echo "Starting RRFDisplay: SPI"
        nohup python $PATH_SCRIPT --interface spi --display ssd1351 --display-height 128 --display-theme blue.cfg --follow F4HWN > $PATH_PID/RRFDisplay_0.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_0.pid
        ;;
    stop) 
        echo "Stopping RRFDisplay SPI"
        kill `cat $PATH_PID/RRFDisplay_0.pid`
        ;;
esac