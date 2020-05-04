#!/bin/sh
echo "+---------------------------+"
echo "Step 1 - Some apt-get install"
echo "+---------------------------+"
apt-get -y install i2c-tools libi2c-dev python-dev python3-lxml
apt-get -y install libfreetype6-dev libjpeg-dev build-essential
echo "+-----------------------+"
echo "Step 2 - Some pip install"
echo "+-----------------------+"
pip3 install --upgrade setuptools
pip3 install requests
pip3 install configparser
pip3 install luma.oled luma.lcd
echo "+------------------+"
echo "Step 3 - Rock'n roll"
echo "+------------------+"
