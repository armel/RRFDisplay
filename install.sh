#!/bin/sh
echo "Update"
apt-get update
echo "Some apt-get install"
apt-get -y install i2c-tools libi2c-dev python-smbus python-pip python-dev python-pil python-lxml
apt-get -y install libfreetype6-dev libjpeg-dev build-essential
echo "Some pip install"
pip3 install --upgrade setuptools
pip3 install requests
pip3 install configparser
pip3 install luma.oled luma.lcd
echo "Rock'n roll"