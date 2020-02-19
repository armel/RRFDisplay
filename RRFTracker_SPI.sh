#!/bin/sh
PATH_SCRIPT='/opt/RRFTracker_Sponik/RRFTracker.py'
PATH_PID='/tmp'

case "$1" in
    start)
        echo "Starting RRFTracker: SPI"
        nohup python $PATH_SCRIPT --interface spi --display ssd1351 --display-height 128 --display-theme theme_rgb.cfg --follow F4HWN > $PATH_PID/RRFTracker_Spotnik_0.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_0.pid
        ;;
    stop) 
        echo "Stopping RRFTracker: SPI"
        kill `cat $PATH_PID/RRFTracker_Spotnik_0.pid`
        ;;
esac