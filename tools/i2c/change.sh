#!/bin/sh
cp /boot/dtb/sun8i-h2-plus-orangepi-zero.dtb .//boot/dtb/sun8i-h2-plus-orangepi-zero.dtb.backup
/usr/bin/dtc -I dts -O dtb ./sun8i-h2-plus-orangepi-zero.dts -o /boot/dtb/sun8i-h2-plus-orangepi-zero.dtb
