#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

case "$1" in
    start)
        echo "Starting RRFDisplay: SPI 0"
        nohup python3 $PATH_SCRIPT --interface spi --display st7735 --spi-device 0 --display-height 160 --display-theme orange.cfg --follow F4HWN > $PATH_PID/RRFDisplay_0.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_0.pid
        echo "Starting RRFDisplay: SPI 1"
        nohup python3 $PATH_SCRIPT --interface spi --display st7735 --spi-device 1 --display-height 160 --display-theme blue.cfg --follow F1ZPX > $PATH_PID/RRFDisplay_1.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_1.pid
        ;;
    stop) 
        echo "Stopping RRFDisplay SPI 0"
        kill `cat $PATH_PID/RRFDisplay_0.pid`
		echo "Stopping RRFDisplay SPI 1"
        kill `cat $PATH_PID/RRFDisplay_1.pid`
        ;;
esac