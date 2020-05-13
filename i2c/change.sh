#!/bin/sh
if [ -z "$1" ]
	then
    	vitesse="400k"
    else
    	vitesse=$1
fi

echo "Change i2C speed to $vitesse"
/usr/bin/dtc -I dts -O dtb ./$vitesse.dts -o /boot/dtb/sun8i-h2-plus-orangepi-zero.dtb
echo "Done !"
echo "Please, reboot now !"