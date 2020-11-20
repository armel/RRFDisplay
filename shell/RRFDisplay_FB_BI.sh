#!/bin/sh
PATH_SCRIPT='/opt/RRFDisplay/RRFDisplay.py'
PATH_PID='/tmp'

cd ..

case "$1" in
    start)
        echo "Starting RRFDisplay: FB"
        nohup python3 $PATH_SCRIPT --interface noop --display linux_framebuffer --display-theme blue_new.cfg/green_new.cfg --display-offset 20/170 --follow F1ZPX/F4HWN > $PATH_PID/RRFDisplay_0.log 2>&1 & echo $! > $PATH_PID/RRFDisplay_0.pid
       ;;
    stop) 
        echo "Stopping RRFDisplay FB"
        kill `cat $PATH_PID/RRFDisplay_0.pid`
        ;;
esac