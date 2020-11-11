#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFDisplay: SPI"
        nohup python3 $PATH_SCRIPT --interface spi --display st7735 --spi-device 0 --display-width 160 --display-theme orange_gray.cfg --follow F4HWN > $PATH_PID/RRFDisplay_0.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_0.pid
        ;;
    stop) 
        echo "Stopping RRFDisplay: SPI"
        kill `cat $PATH_PID/RRFDisplay_0.pid`
        ;;
esac