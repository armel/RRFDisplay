#!/bin/sh
PATH_SCRIPT='/opt/RRFTracker_Spotnik/RRFTracker.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFTracker: SPI"
        nohup python $PATH_SCRIPT --interface spi --display ssd1351 --display-height 128 --display-theme theme_bleu.cfg --follow F1ZPX > $PATH_PID/RRFTracker_Spotnik_0.log 2>&1 & echo $! > $PATH_PID/RRFTracker_Spotnik_0.pid
        ;;
    stop) 
        echo "Stopping RRFTracker: SPI"
        kill `cat $PATH_PID/RRFTracker_Spotnik_0.pid`
        ;;
esac